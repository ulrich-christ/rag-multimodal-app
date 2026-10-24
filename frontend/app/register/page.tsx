"use client"

import {useState} from "react"
import {useRouter} from "next/navigation"
import Link from "next/link"
import {apiFetch} from "@/lib/api"

export default function RegisterPage(){
    const [email, setEmail] = useState("")
    const [password, setPassword] =useState("")
    const [error, setError] = useState("")
    const [loading, setLoading] = useState(false)
    const router = useRouter();

    async function handleSubmit(e:React.FormEvent){
        e.preventDefault();
        setError("")
        setLoading(true)

        try{await apiFetch("/auth/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password }),
        });
        router.push("/login");

        }catch (err) { setError((err as Error).message) }
        finally{
            setLoading(false)
        }
    }

    const inputClass = "w-full bg-gray-800 border border-gray-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"

    return (
        <main className="flex flex-1 items-center justify-center p-4">
            <form onSubmit={handleSubmit} className="flex w-full max-w-sm flex-col gap-3">
                <h1 className="text-xl font-semibold">Registration</h1>

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
                    {loading ? "Creation..." : "Creer un compte"}
                </button>

                {error && <p className="text-xs text-red-400">{error}</p>}

                <p className="text-sm">
                   Already have an account <Link href="/login" className="text-blue-500">Login</Link>
                </p>
            </form>
        </main>
    )
}
