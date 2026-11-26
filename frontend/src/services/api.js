const base = "/api";
const failures = {404:"Registro não encontrado.",409:"A operação conflita com o estado atual do registro.",422:"Confira os campos informados."};
export async function request(path, {method="GET", body, signal, params}={}) {
  const query = new URLSearchParams();
  for (const [key,value] of Object.entries(params || {})) {
    if (value !== "" && value != null) query.set(key, value);
  }
  let response;
  try {
    response = await fetch(base + path + (query.size ? "?" + query : ""), {
      method, signal, headers: body ? {"Content-Type":"application/json"} : undefined,
      body: body ? JSON.stringify(body) : undefined
    });
  } catch (error) {
    if (error.name === "AbortError") throw error;
    throw new Error("Não foi possível conectar à API. Verifique a conexão e tente novamente.");
  }
  if (!response.ok) {
    const {detail} = await response.json().catch(()=>({}));
    let message = failures[response.status] || "Serviço indisponível. Tente novamente.";
    if (response.status < 500 && typeof detail === "string") message = detail;
    if (Array.isArray(detail)) message = detail.map(e => [e.loc?.slice(1).join("."), e.msg].filter(Boolean).join(": ")).join(" · ");
    const error = new Error(message);
    error.status = response.status;
    throw error;
  }
  return response.status === 204 ? null : response.json();
}
function collection(path) {
  return {
    list:(params,signal)=>request(path,{params,signal}),
    get:(id,signal)=>request(path+"/"+id,{signal}),
    create:body=>request(path,{method:"POST",body}),
    edit:(id,body)=>request(path+"/"+id,{method:"PUT",body}),
    remove:id=>request(path+"/"+id,{method:"DELETE"})
  };
}
export const requesters = collection("/requesters");
export const categories = collection("/categories");
export const tickets = {
  ...collection("/tickets"),
  transition:(id,body)=>request("/tickets/"+id+"/status",{method:"PATCH",body}),
  history:(id,signal)=>request("/tickets/"+id+"/history",{signal}),
  notices:(id,signal)=>request("/tickets/"+id+"/notifications",{signal})
};
export const dashboard = signal=>request("/dashboard",{signal});
export const notifications = {
  list:(params,signal)=>request("/notifications",{params,signal}),
  modes:signal=>request("/notifications/channels",{signal}),
  retry:id=>request("/notifications/"+id+"/retry",{method:"POST"})
};
async function allPages(service,signal) {
  const items=[];
  for(let page=1;;page++) {
    const batch=await service.list({page,page_size:100},signal);
    items.push(...batch.items);
    if(items.length>=batch.total || !batch.items.length) return items;
  }
}
export const catalogs = signal=>Promise.all([allPages(requesters,signal),allPages(categories,signal)]).then(([people,groups])=>({people,groups}));
