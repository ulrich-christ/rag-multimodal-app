const API_URL = process.env.NEXT_PUBLIC_API_URL

export async function apiFetch(path:string, options:RequestInit={}){
    const token = localStorage.getItem("token")
    const headers = new Headers(options.headers)

    if (token) headers.set("Authorization", `Bearer ${token}`);

    const res = await fetch(`${API_URL}${path}`, {...options, headers});


    if(res.status===401){
        localStorage.removeItem("token");
        window.location.href = "/login"
        throw new Error("Not Authenticated");
        
    }

    if (!res.ok){
        const err = await res.json().catch(()=>({}))
        throw new Error(err.detail ?? "Request failed");
        
    }
    return res.json()
}