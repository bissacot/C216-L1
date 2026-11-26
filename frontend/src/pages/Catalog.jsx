import {Pencil,Plus,Search,Trash2} from "lucide-react";
import {useState} from "react";
import {useOutletContext} from "react-router-dom";
import {Filters} from "../components/Filters";
import {Alert,Dialog,Empty,Field,Pages,PageTitle,Panel,State} from "../components/ui";
import {useAction,useList,useResource} from "../hooks/resources";
import {categories,requesters} from "../services/api";
import {date} from "../utils/format";
const specs={requesters:{name:"Solicitantes",one:"solicitante",api:requesters,description:"Gerencie as pessoas que solicitam suporte à equipe.",fields:[["name","Nome","text",150],["email","E-mail","email",254],["department","Departamento","text",150]]},categories:{name:"Categorias",one:"categoria",api:categories,description:"Organize os chamados por área de suporte.",fields:[["name","Nome","text",100],["description","Descrição","textarea"]]}};
function Editor({spec,record,mode,close,done}){
  const [draft,set]=useState(record||{}),[invalid,setInvalid]=useState(""),action=useAction();
  const remove=mode==="delete";
  function submit(e){e.preventDefault();const body=Object.fromEntries(spec.fields.map(([key])=>[key,draft[key]?.trim()||null]));
    if(!remove && (!body.name || ("email" in body && !body.email))){setInvalid("Preencha os campos obrigatórios.");return}setInvalid("");
    action.run(()=>remove?spec.api.remove(record.id):record?spec.api.edit(record.id,body):spec.api.create(body),done,e=>e.status===409?(remove?"Há chamados vinculados a este cadastro. A exclusão foi impedida.":"Já existe um cadastro com o mesmo nome ou e-mail único."):e.message)
  }
  return <Dialog title={(remove?"Excluir ":record?"Editar ":"Cadastrar ")+spec.one} onClose={close} busy={action.busy}><form onSubmit={submit} className="form-grid">{remove?<p>Confirma a exclusão de <strong>{record.name}</strong>?</p>:spec.fields.map(([key,label,type,max])=><Field key={key} label={label}>{type==="textarea"?<textarea rows={3} value={draft[key]||""} onChange={e=>set({...draft,[key]:e.target.value})}/>:<input type={type} maxLength={max} required={key==="name"||key==="email"} value={draft[key]||""} onChange={e=>set({...draft,[key]:e.target.value})}/>}</Field>)}<Alert message={invalid||action.error}/><div className="form-actions"><button className="button" type="button" onClick={close} disabled={action.busy}>Voltar</button><button className={"button "+(remove?"danger":"primary")} type="submit" disabled={action.busy}>{remove?"Confirmar exclusão":"Salvar"}</button></div></form></Dialog>
}
export default function Catalog({kind}){
 const spec=specs[kind],list=useList(),{notify}=useOutletContext(),[edit,setEdit]=useState(null);
 const r=useResource(kind+"?"+list.key,signal=>spec.api.list({q:list.values.q,page:list.page,page_size:10},signal));
 function done(){notify(edit.mode==="delete"?"Cadastro excluído.":"Cadastro salvo.");if(edit.mode==="delete" && r.data?.items.length===1 && list.page>1)list.go(list.page-1);else r.refresh();setEdit(null)}
 return <><PageTitle title={spec.name} description={spec.description}><button type="button" className="button primary" onClick={()=>setEdit({mode:"new"})}><Plus size={16}/>Cadastrar {spec.one}</button></PageTitle>
 <Panel title={"Lista de "+spec.name.toLowerCase()} aside={<Search size={17}/>}><Filters key={list.key} values={list.values} apply={list.apply} searchLabel={"Buscar "+spec.one}/><State resource={r}>{d=><>{d.items.length?<div className="table-scroll"><table><thead><tr>{spec.fields.map(([key,label])=><th key={key}>{label}</th>)}<th>Criação</th><th>Ações</th></tr></thead><tbody>{d.items.map(row=><tr key={row.id}>{spec.fields.map(([k])=><td key={k}>{row[k]||"—"}</td>)}<td>{date(row.created_at)}</td><td><div className="actions"><button type="button" className="icon-button" aria-label={"Editar "+row.name} onClick={()=>setEdit({mode:"edit",record:row})}><Pencil size={15}/></button><button type="button" className="icon-button destructive" aria-label={"Excluir "+row.name} onClick={()=>setEdit({mode:"delete",record:row})}><Trash2 size={15}/></button></div></td></tr>)}</tbody></table></div>:<Empty title="Nenhum cadastro encontrado"/>}<Pages data={d} go={list.go}/></>}</State></Panel>{edit&&<Editor spec={spec} {...edit} close={()=>setEdit(null)} done={done}/>}</>
}
