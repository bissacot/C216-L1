import {Mail,MessageSquare,RotateCcw} from "lucide-react";
import {useState} from "react";
import {Link,useOutletContext} from "react-router-dom";
import {notifications} from "../services/api";
import {useAction} from "../hooks/resources";
import {channels,date,modes,ticketCode} from "../utils/format";
import {Alert,Badge,Dialog,Empty} from "./ui";
export function ChannelModes({values}){return <div className="channel-modes">{Object.entries(values).map(([channel,mode])=><span key={channel}>{channel==="EMAIL"?<Mail size={14}/>:<MessageSquare size={14}/>}<strong>{channels[channel]}</strong> · {modes[mode]}</span>)}</div>}
export function Deliveries({items,refresh}){
  const [selected,setSelected]=useState(null),action=useAction(),{notify}=useOutletContext();
  function retry(){action.run(()=>notifications.retry(selected.id),()=>{setSelected(null);notify("Nova tentativa registrada para processamento.");refresh()})}
  if(!items.length)return <Empty title="Nenhuma notificação encontrada">As entregas de cada chamado aparecem após a abertura.</Empty>;
  return <div className="deliveries">{items.map(n=>{const Icon=n.channel==="EMAIL"?Mail:MessageSquare;
    return <article className="delivery" key={n.id}><div className="delivery-head"><div className="delivery-title"><span className="channel-icon"><Icon size={18}/></span><div><strong>{channels[n.channel]}</strong><Link to={"/tickets/"+n.ticket_id}>Chamado {ticketCode(n.ticket_id)}</Link></div></div><Badge value={n.status}>{n.processing?"Em processamento":n.status==="SENT"&&n.delivery_mode==="MOCK"?"Simulação concluída":undefined}</Badge></div>
    <dl className="delivery-meta"><div><dt>Destinatário lógico</dt><dd>{n.recipient}</dd></div><div><dt>Modo da tentativa</dt><dd>{modes[n.delivery_mode] || (n.attempt_count?"Não registrado":"Sem tentativa")}</dd></div><div><dt>Tentativas</dt><dd>{n.attempt_count}</dd></div><div><dt>Última tentativa</dt><dd>{date(n.last_attempt_at)}</dd></div><div><dt>Data de envio</dt><dd>{date(n.sent_at)}</dd></div></dl>
    {n.last_error&&<p className="delivery-error">{n.last_error}</p>}{n.next_attempt_at&&<p className="muted">Próxima tentativa em {date(n.next_attempt_at)}</p>}
    {n.status==="FAILED"&&!n.processing&&<button type="button" className="button small" onClick={()=>{action.clear();setSelected(n)}}><RotateCcw size={14}/>Solicitar nova tentativa</button>}</article>})}
    {selected&&<Dialog title="Reagendar notificação" busy={action.busy} onClose={()=>setSelected(null)}><p>Reagendar a entrega por {channels[selected.channel]} do chamado {ticketCode(selected.ticket_id)}?</p><Alert message={action.error}/><div className="form-actions"><button className="button" type="button" disabled={action.busy} onClick={()=>setSelected(null)}>Voltar</button><button className="button primary" type="button" disabled={action.busy} onClick={retry}>Confirmar reenvio</button></div></Dialog>}</div>
}
