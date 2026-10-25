let accessToken=sessionStorage.getItem('torque-token');
export function setToken(value){accessToken=value;value?sessionStorage.setItem('torque-token',value):sessionStorage.removeItem('torque-token');}
export function hasToken(){return Boolean(accessToken);}
export async function api(path,options={}) {
  const response=await fetch(`/api${path}`,{...options,headers:{'Content-Type':'application/json',...(accessToken?{Authorization:`Bearer ${accessToken}`} :{}),...options.headers}});
  if(response.status===204)return null;
  const data=await response.json().catch(()=>({detail:'Unexpected server response'}));
  if(!response.ok){
    if(response.status===401 && !path.startsWith('/auth/login')){setToken(null);window.dispatchEvent(new Event('session-expired'));}
    const message=Array.isArray(data.detail)?data.detail.map(e=>`${e.loc.at(-1)}: ${e.msg}`).join('; '):data.detail;
    throw new Error(message||'The request could not be completed');
  }
  return data;
}
