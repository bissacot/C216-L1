import {BrowserRouter,Link,Route,Routes} from "react-router-dom";
import Shell from "./layouts/Shell";
import Dashboard from "./pages/Dashboard";
import Tickets from "./pages/Tickets";
import TicketForm from "./pages/TicketForm";
import TicketDetail from "./pages/TicketDetail";
import Catalog from "./pages/Catalog";
import Notifications from "./pages/Notifications";
export function AppRoutes(){return <Routes><Route element={<Shell/>}><Route index element={<Dashboard/>}/><Route path="tickets" element={<Tickets/>}/><Route path="tickets/new" element={<TicketForm key="new"/>}/><Route path="tickets/:id/edit" element={<TicketForm key="edit"/>}/><Route path="tickets/:id" element={<TicketDetail/>}/><Route path="requesters" element={<Catalog key="people" kind="requesters"/>}/><Route path="categories" element={<Catalog key="groups" kind="categories"/>}/><Route path="notifications" element={<Notifications/>}/><Route path="*" element={<section><h1>Página não encontrada</h1><Link className="text-button" to="/">Voltar ao dashboard</Link></section>}/></Route></Routes>}
export default function App(){return <BrowserRouter><AppRoutes/></BrowserRouter>}
