const tenant=document.querySelector('#tenant')
const env=document.querySelector('#env')
const loc=document.querySelector('#loc')
const manage=document.querySelector('#manage')
const subtype=document.querySelector('#subtype')
const app=document.querySelector('#app')
const subscription=document.querySelector('#sub')
const rg=document.querySelector('#rg')
const vnet=document.querySelector('#vnet')
const subnet=document.querySelector('#subnet')

document.addEventListener("DOMContentLoaded", async function () {
    const res=await fetch('http://127.0.0.1:5000/get_tenant')
    const data= await res.json()
    tenant.innerHTML=""
    tenant.innerHTML="<option value=''>-- None --</option>"
    for(let i of data){
        const opt=document.createElement('option')
        opt.value=i
        opt.textContent=i
        tenant.append(opt)
    }
});

tenant.addEventListener('change',async(e)=>{
    const res = await fetch('http://127.0.0.1:5000/get_env', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            tenant: e.target.value
        })
    });

    const data = await res.json();
    env.innerHTML=""
    env.innerHTML="<option value=''>-- None --</option>"
    for(let i of data.env){
        const opt=document.createElement('option')
        opt.value=i
        opt.textContent=i
        env.append(opt)
    }
})
env.addEventListener('change',async(e)=>{
    const res = await fetch('http://127.0.0.1:5000/get_loc', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            env: e.target.value,
            tenant:tenant.value
        })
    });

    const data = await res.json();
    loc.innerHTML=""
    loc.innerHTML="<option value=''>-- None --</option>"
    for(let i of data.loc){
        const opt=document.createElement('option')
        opt.value=i
        opt.textContent=i
        loc.append(opt)
    }
})
loc.addEventListener('change',async(e)=>{
    const res = await fetch('http://127.0.0.1:5000/get_manage', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            loc: e.target.value,
            env:env.value,
            tenant:tenant.value
        })
    });

    const data = await res.json();
    manage.innerHTML=""
    manage.innerHTML="<option value=''>-- None --</option>"
    for(let i of data.manage){
        const opt=document.createElement('option')
        opt.value=i
        opt.textContent=i
        manage.append(opt)
    }
})
manage.addEventListener('change',async(e)=>{
    const res = await fetch('http://127.0.0.1:5000/get_subtype', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            manage: e.target.value,
            loc:loc.value,
            env:env.value,
            tenant:tenant.value
        })
    });

    const data = await res.json();
    subtype.innerHTML=""
    subtype.innerHTML="<option value=''>-- None --</option>"
    for(let i of data.subtype){
        const opt=document.createElement('option')
        opt.value=i
        opt.textContent=i
        subtype.append(opt)
    }
})
subtype.addEventListener('change',async(e)=>{
    const res = await fetch('http://127.0.0.1:5000/get_app', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            subtype: e.target.value,
            manage:manage.value,
            loc:loc.value,
            env:env.value,
            tenant:tenant.value
        })
    });

    const data = await res.json();
    app.innerHTML=""
    app.innerHTML="<option value=''>-- None --</option>"
    for(let i of data.apps){
        const opt=document.createElement('option')
        opt.value=i
        opt.textContent=i
        app.append(opt)
    }
})
app.addEventListener('change',async(e)=>{
    const res = await fetch('http://127.0.0.1:5000/get_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            app: e.target.value,
            subtype:subtype.value,
            manage:manage.value,
            loc:loc.value,
            env:env.value,
            tenant:tenant.value
        })
    });

    const data = await res.json();
    
    data.data.map(val=>{
        subnet.value=val.subnet
        vnet.value=val.vnet
        subscription.value=val.sub
        rg.value=val.rg
    })
    
    
   
})
