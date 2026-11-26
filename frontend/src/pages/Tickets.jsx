import {ChevronRight,ListFilter} from "lucide-react";
import {Link} from "react-router-dom";
import {Filters} from "../components/Filters";
import {Alert,Badge,Empty,NewTicket,Pages,PageTitle,Panel,State} from "../components/ui";
import {useList,useResource} from "../hooks/resources";
import {catalogs,tickets} from "../services/api";
import {date,localBoundary,priorities,statuses,ticketCode} from "../utils/format";
export default function Tickets(){
  const list=useList({sort_by:"opened_at",order:"desc"});
  const refs=useResource("catalogs",catalogs);
  const r=useResource("tickets?"+list.key,signal=>tickets.list({...list.values,page:list.page,page_size:10,opened_from:localBoundary(list.values.opened_from),opened_to:localBoundary(list.values.opened_to,true)},signal));
  const people=Object.fromEntries((refs.data?.people||[]).map(x=>[x.id,x.name]));
  const groups=Object.fromEntries((refs.data?.groups||[]).map(x=>[x.id,x.name]));
  return <><PageTitle title="Central de chamados" description="Pesquise, acompanhe e gerencie as solicitações de suporte."><NewTicket/></PageTitle><Panel title="Filtros de chamados" aside={<ListFilter size={18}/>}><Alert message={refs.error}/><Filters key={list.key} values={list.values} apply={list.apply} searchLabel="Título ou descrição" sort fields={[{key:"status",label:"Status",options:statuses},{key:"priority",label:"Prioridade",options:priorities},{key:"category_id",label:"Categoria",options:groups},{key:"requester_id",label:"Solicitante",options:people},{key:"assignee",label:"Responsável"},{key:"opened_from",label:"Abertos desde",type:"date"},{key:"opened_to",label:"Abertos até",type:"date"}]}/></Panel>
  <Panel title="Lista de chamados"><State resource={r}>{d=><>{d.items.length?<div className="table-scroll"><table><thead><tr>{["Chamado","Solicitante","Categoria","Prioridade","Status","Responsável","Abertura","Ações"].map(v=><th key={v}>{v}</th>)}</tr></thead><tbody>{d.items.map(t=><tr key={t.id}><td><Link className="ticket-link" to={"/tickets/"+t.id}><small>{ticketCode(t.id)}</small>{t.title}</Link></td><td>{people[t.requester_id]??"#"+t.requester_id}</td><td>{groups[t.category_id]??"#"+t.category_id}</td><td><Badge value={t.priority}/></td><td><Badge value={t.status}/></td><td>{t.assignee||"Sem responsável"}</td><td>{date(t.opened_at)}</td><td><Link className="icon-button" aria-label={"Detalhes do chamado "+t.id} to={"/tickets/"+t.id}><ChevronRight size={16}/></Link></td></tr>)}</tbody></table></div>:<Empty title="Nenhum chamado encontrado">Revise os filtros ou abra um novo chamado.</Empty>}<Pages data={d} go={list.go}/></>}</State></Panel></>
}
