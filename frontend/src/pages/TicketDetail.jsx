import {ArrowLeft,CheckCheck,History,Mail,Pencil,Play,Trash2,X} from "lucide-react";
import {useState} from "react";
import {Link,useNavigate,useOutletContext,useParams} from "react-router-dom";
import {ChannelModes,Deliveries} from "../components/Deliveries";
import {Alert,Badge,Dialog,Empty,Field,PageTitle,Panel,Refresh,State} from "../components/ui";
import {useAction,useResource} from "../hooks/resources";
import {categories,notifications,requesters,tickets} from "../services/api";
import {active,date,priorities,statuses,ticketCode} from "../utils/format";
const actions={IN_PROGRESS:"Iniciar atendimento",RESOLVED:"Resolver chamado",CANCELLED:"Cancelar chamado",delete:"Excluir chamado"};
const fields={status:"Status",assignee:"Responsável",resolution:"Solução",title:"Título",description:"Descrição",priority:"Prioridade",requester_id:"Solicitante",category_id:"Categoria",resolved_at:"Data de resolução"};
function describe(field,value){if(value==null)return "—";if(field==="status")return statuses[value]||value;if(field==="priority")return priorities[value]||value;if(field==="resolved_at")return date(value);return value}
function Change({type,ticket,close,done}){
  const [text,setText]=useState(type==="IN_PROGRESS"?ticket.assignee||"":"");
  const [invalid,setInvalid]=useState(""),a=useAction();
  const destructive=type==="delete"||type==="CANCELLED";
  function submit(e){e.preventDefault();const value=text.trim();
    if(!destructive&&!value){setInvalid("Preencha o campo obrigatório.");return}setInvalid("");
    const body={status:type};
    if(type==="IN_PROGRESS")body.assignee=value;if(type==="RESOLVED")body.resolution=value;
    a.run(()=>type==="delete"?tickets.remove(ticket.id):tickets.transition(ticket.id,body),done)
  }
  return <Dialog title={actions[type]} onClose={close} busy={a.busy}><form className="form-grid" onSubmit={submit}>
    {type==="IN_PROGRESS" && <Field label="Responsável"><input required maxLength={150} value={text} onChange={e=>setText(e.target.value)}/></Field>}
    {type==="RESOLVED" && <Field label="Descrição da solução"><textarea required rows={4} value={text} onChange={e=>setText(e.target.value)}/></Field>}
    {destructive&&<p>{type==="delete"?"Excluir definitivamente o chamado, o histórico e as notificações vinculadas?":"Confirmar o cancelamento deste chamado?"}</p>}
    <Alert message={invalid||a.error}/><div className="form-actions"><button type="button" className="button" disabled={a.busy} onClick={close}>Voltar</button><button type="submit" className={"button "+(destructive?"danger":"primary")} disabled={a.busy}>{type==="delete"?"Confirmar exclusão":"Confirmar"}</button></div></form></Dialog>
}
function Related({id}){
  const r=useResource("related/"+id,async signal=>{const [items,modes]=await Promise.all([tickets.notices(id,signal),notifications.modes(signal)]);return {items,modes}},30000);
  return <Panel title="Notificações do chamado" aside={<Refresh resource={r}/>}><State resource={r}>{({items,modes})=><><ChannelModes values={modes}/><Deliveries items={items} refresh={r.refresh}/></>}</State></Panel>
}
export default function TicketDetail(){
  const {id}=useParams(),[change,setChange]=useState(null),navigate=useNavigate(),{notify}=useOutletContext();
  const r=useResource("detail/"+id,async signal=>{
    const [ticket,history]=await Promise.all([tickets.get(id,signal),tickets.history(id,signal)]);
    const [person,group]=await Promise.all([requesters.get(ticket.requester_id,signal),categories.get(ticket.category_id,signal)]);
    return {ticket,history,person,group}
  });
  function done(){notify(change==="delete"?"Chamado excluído.":"Atendimento atualizado.");if(change==="delete")navigate("/tickets");else r.refresh();setChange(null)}
  return <><Link className="back" to="/tickets"><ArrowLeft size={15}/>Central de chamados</Link><State resource={r}>{({ticket:t,history,person,group})=><><div className="ticket-kicker">Chamado {ticketCode(t.id)}</div><PageTitle title={t.title}><Badge value={t.priority}/><Badge value={t.status}/></PageTitle>
  <Panel title="Informações do chamado" aside={active(t.status)&&<Link className="text-button" to={"/tickets/"+id+"/edit"}><Pencil size={14}/>Editar chamado</Link>}><p className="preserve">{t.description}</p><dl className="detail-grid">{[["Solicitante",person.name],["E-mail",person.email],["Departamento",person.department],["Categoria",group.name],["Responsável",t.assignee],["Abertura",date(t.opened_at)],["Última atualização",date(t.updated_at)],["Data da resolução",date(t.resolved_at)]].map(([k,v])=><div key={k}><dt>{k}</dt><dd>{v||"—"}</dd></div>)}</dl>{t.resolution&&<div className="solution"><strong>Solução registrada</strong><p className="preserve">{t.resolution}</p></div>}
  {t.status!=="RESOLVED"&&<div className="action-strip">{t.status==="OPEN" && <button className="button primary" type="button" onClick={()=>setChange("IN_PROGRESS")}><Play size={15}/>{actions.IN_PROGRESS}</button>}{t.status==="IN_PROGRESS"&&<button className="button primary" type="button" onClick={()=>setChange("RESOLVED")}><CheckCheck size={15}/>{actions.RESOLVED}</button>}{active(t.status)&&<button className="button" type="button" onClick={()=>setChange("CANCELLED")}><X size={15}/>{actions.CANCELLED}</button>}{t.status==="CANCELLED"&&<button className="button danger" type="button" onClick={()=>setChange("delete")}><Trash2 size={15}/>{actions.delete}</button>}</div>}</Panel>
  <Panel title="Histórico de alterações" aside={<History size={17}/>}><ol className="timeline">{history.map(h=><li key={h.id}><span className="timeline-dot"/><div><strong>{fields[h.field_name]||h.field_name}</strong><p>{describe(h.field_name,h.old_value)} → {describe(h.field_name,h.new_value)}</p><small>{date(h.changed_at)}{h.changed_by&&" · "+h.changed_by}</small></div></li>)}</ol>{!history.length&&<Empty title="Nenhuma alteração registrada"/>}</Panel>
  <Related id={id}/>{change&&<Change type={change} ticket={t} close={()=>setChange(null)} done={done}/>}</>}</State></>
}
