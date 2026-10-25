import React from 'react';
import { ArrowUpRight, Fuel, CalendarDays, Pencil, Plus, Trash2 } from 'lucide-react';
import { CarArt } from './CarArt';
export const money=(amount)=>new Intl.NumberFormat('en-IN',{style:'currency',currency:'INR',maximumFractionDigits:0}).format(amount);
export function VehicleCard({car,admin,onPurchase,onEdit,onRestock,onDelete}) {
  return <article className="vehicle-card">
    <div className={`vehicle-visual tone-${car.color.toLowerCase()}`}><span className="category-chip">{car.category}</span><span className={`stock-chip ${car.quantity===0?'empty':car.quantity<=2?'low':''}`}><i/>{car.quantity===0?'Out of stock':`${car.quantity} in stock`}</span><CarArt car={car}/><span className="illustration-label">VEHICLE ILLUSTRATION</span></div>
    <div className="vehicle-info"><p className="make-label">{car.make}</p><h3>{car.model}</h3><div className="specs"><span><CalendarDays size={13}/>{car.year}</span><span><Fuel size={13}/>{car.fuel}</span><span><i style={{background:({Teal:'#438b86',Blue:'#4573a2',Red:'#b74f48',Black:'#424b4a',White:'#ddd',Silver:'#9baea9'})[car.color]||'#859c91'}}/>{car.color}</span></div><div className="price-row"><div><small>LIST PRICE</small><strong>{money(car.price)}</strong></div><button className="purchase-button" onClick={()=>onPurchase(car)} disabled={car.quantity===0}>{car.quantity===0?'Out of stock':<>Purchase <ArrowUpRight size={16}/></>}</button></div>
    {admin&&<div className="admin-actions"><button onClick={()=>onEdit(car)} aria-label={`Edit ${car.model}`}><Pencil size={13}/>Edit</button><button onClick={()=>onRestock(car)} aria-label={`Restock ${car.model}`}><Plus size={14}/>Restock</button><button className="delete-action" onClick={()=>onDelete(car)} aria-label={`Delete ${car.model}`}><Trash2 size={13}/><span>Delete</span></button></div>}</div>
  </article>;
}
