import React from 'react';
const tones={Teal:'#438b86',Blue:'#4573a2',Red:'#b74f48',Black:'#424b4a',White:'#d5dcd8',Silver:'#9baea9'};
/** Original vector illustration: no remote image service or asset download required. */
export function CarArt({car={}, hero=false}) {
  const color=tones[car.color]||'#6f9490';
  const suv=['SUV','MPV','Truck'].includes(car.category);
  return <svg viewBox="0 0 540 250" role="img" aria-label={`${car.make||''} ${car.model||'Vehicle'} illustration`} className={hero?'car-art hero-car':'car-art'}>
    <ellipse cx="277" cy="213" rx="213" ry="13" fill="#143d35" opacity=".10"/>
    <path d={suv?'M70 167L91 116Q96 106 113 104L152 57Q164 45 187 45H347Q366 45 385 65L425 110L475 126Q490 132 494 151L497 184Q495 194 480 194H69Q55 190 58 178Z':'M65 166L81 137Q88 125 116 119L175 65Q188 54 213 54H318Q339 54 360 71L415 115L472 134Q490 142 493 165L491 185Q487 194 472 194H67Q55 191 57 178Z'} fill={color} stroke="#213b37" strokeWidth="2"/>
    <path d={suv?'M118 106L163 62Q168 57 189 57H248V106Z':'M127 119L184 74Q194 66 214 66H249V116Z'} fill="#183d42"/>
    <path d={suv?'M261 57H344Q356 57 370 73L399 107H261Z':'M261 66H317Q331 66 348 80L392 116H261Z'} fill="#23484c"/>
    <path d={suv?'M174 62L145 100H226L236 62Z':'M194 72L148 110H227L238 72Z'} fill="#88b5b3" opacity=".23"/>
    <path d="M270 64L281 104H381L344 70Z" fill="#b2d4cc" opacity=".12"/>
    <path d="M77 143L112 140L104 154H72Z" fill="#ebf3df"/>
    <path d="M453 136L479 145L484 157L453 152Z" fill="#f0c3a4"/>
    <path d="M122 165H419" stroke="#21463f" opacity=".35" strokeWidth="2"/>
    <path d="M250 119V180M389 123L409 180M142 127L125 179" stroke="#284c45" opacity=".48" strokeWidth="1.5"/>
    <rect x="268" y="128" width="22" height="4" rx="2" fill="#e3eee7" opacity=".8"/>
    <rect x="164" y="130" width="22" height="4" rx="2" fill="#e3eee7" opacity=".8"/>
    <path d="M68 180H489" stroke="#213b37" strokeWidth="9"/>
    {[143,409].map(x=><g key={x}><circle cx={x} cy="185" r="39" fill="#172a29"/><circle cx={x} cy="185" r="28" fill="#b5c5bf"/><circle cx={x} cy="185" r="20" fill="#344b47"/>{[0,60,120].map(a=><path key={a} d={`M${x} 163V207`} stroke="#ccdad3" strokeWidth="6" transform={`rotate(${a} ${x} 185)`}/>)}<circle cx={x} cy="185" r="7" fill="#7d948b"/></g>)}
    <path d="M421 117L409 109H394L400 121Z" fill="#172f2c"/>
    <path d="M95 129Q273 120 443 130" fill="none" stroke="#e7f6e8" opacity=".35" strokeWidth="2"/>
  </svg>;
}
