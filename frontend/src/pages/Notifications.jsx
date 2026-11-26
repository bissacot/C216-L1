import {ChannelModes,Deliveries} from "../components/Deliveries";
import {Filters} from "../components/Filters";
import {Pages,PageTitle,Panel,Refresh,State} from "../components/ui";
import {useList,useResource} from "../hooks/resources";
import {notifications} from "../services/api";
import {channels,deliveryStatuses} from "../utils/format";
export default function Notifications(){
  const list=useList();
  const r=useResource("notices?"+list.key,async signal=>{const [page,modes]=await Promise.all([notifications.list({...list.values,page:list.page,page_size:10},signal),notifications.modes(signal)]);return {page,modes}},30000);
  return <><PageTitle title="Central de notificações" description="Consulte as entregas por canal e acompanhe as tentativas."><Refresh resource={r}/></PageTitle><Panel title="Filtros de entrega"><Filters key={list.key} values={list.values} apply={list.apply} fields={[{key:"channel",label:"Canal",options:channels},{key:"status",label:"Status",options:deliveryStatuses},{key:"ticket_id",label:"ID do chamado",type:"number"}]}/></Panel><State resource={r}>{({page,modes})=><Panel title="Entregas" aside={<span className="muted">Atualização a cada 30 s</span>}><ChannelModes values={modes}/><Deliveries items={page.items} refresh={r.refresh}/><Pages data={page} go={list.go}/></Panel>}</State></>
}
