"use client"

import {useState} from "react"
import {useRouter} from "next/navigation"
import Link from "next/link"

export default function LoginPage(){
    const [email, setEmail] = useState("")
    const [password, setPassword] =useState("")
    const [error, setError] = useState("")
    const [loading, setLoading] = useState(false)
    const router = useRouter();

    async function handleSubmit(e:React.FormEvent){
        e.preventDefault();
        setError("")
        setLoading(true)

        try{
            const res =  await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/login`,{
                method:"POST",  
                body:new URLSearchParams({username:email, password})
            });
            const data = await res.json();

            if(!res.ok){   
                setError(data.detail?? "Connection Error")
                return    
            }

            localStorage.setItem("token",data.access_token)
            router.push("/documents");

        }catch{
            setError("Server Not found")
        }finally{
            setLoading(false)
        }
    }

    const inputClass = "w-full bg-gray-800 border border-gray-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"

    return (
        <main className="flex flex-1 items-center justify-center p-4">
            <form onSubmit={handleSubmit} className="flex w-full max-w-sm flex-col gap-3">
                <h1 className="text-xl font-semibold">Connexion</h1>

                {}
                <input
                    type="email"
                    placeholder="Email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className={inputClass}
                />
                <input
                    type="password"
                    placeholder="Mot de passe"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className={inputClass}
                />

                <button
                    type="submit"
                    disabled={loading}
                    className="w-full rounded-lg bg-blue-600 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
                >
                    {loading ? "Connexion..." : "Se connecter"}
                </button>

                {/* Affiché seulement s'il y a une erreur */}
                {error && <p className="text-xs text-red-400">{error}</p>}

                <p className="text-sm">
                    Pas de compte ? <Link href="/register" className="text-blue-500">Créer un compte</Link>
                </p>
            </form>
        </main>
    )
}
