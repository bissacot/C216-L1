import {Search,SlidersHorizontal} from "lucide-react";
import {useState} from "react";
import {Field,Options} from "./ui";
export function Filters({values,apply,fields=[],searchLabel,sort=false}){
  const [draft,setDraft]=useState(values);
  function input(name){return {value:draft[name]??"",onChange:e=>setDraft({...draft,[name]:e.target.value})}}
  return <form className="filters" onSubmit={e=>{e.preventDefault();const next={};for(const [k,v] of Object.entries(draft))if(k!=="page" && String(v).trim())next[k]=String(v).trim();apply(next)}}>
  {searchLabel && <Field label="Pesquisa"><div className="search-box"><Search size={16}/><input type="search" maxLength={200} placeholder={searchLabel} {...input("q")}/></div></Field>}
  {fields.map(f=><Field key={f.key} label={f.label}>{f.options?<select {...input(f.key)}><option value="">{f.placeholder||"Todos"}</option><Options values={f.options}/></select>:<input type={f.type || "text"} step={f.type==="number"?1:undefined} min={f.key==="opened_to"?draft.opened_from:undefined} max={f.key==="opened_from"?draft.opened_to:undefined} {...input(f.key)}/>}</Field>)}
  {sort && <><Field label="Ordenar por"><select {...input("sort_by")}><Options values={{opened_at:"Abertura",updated_at:"Atualização",id:"Identificador",title:"Título",priority:"Prioridade",status:"Status"}}/></select></Field><Field label="Ordem"><select {...input("order")}><Options values={{desc:"Decrescente",asc:"Crescente"}}/></select></Field></>}
  <div className="filter-actions"><button className="button" type="submit"><SlidersHorizontal size={15}/>Aplicar filtros</button><button className="text-button" type="button" onClick={()=>{setDraft({});apply({})}}>Limpar</button></div></form>
}
