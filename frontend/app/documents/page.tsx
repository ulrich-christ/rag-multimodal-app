"use client"

import {useState, useEffect} from "react"
import {apiFetch} from "@/lib/api"
import {useRouter} from "next/navigation"
import Link from "next/link"   // AJOUTÉ : pour le lien "Ouvrir"

type Doc = {
    id:number;
    filename:string;
    status:"pending" | "processing" | "ready" | "failed" ;
    chunk_count:number
    created_at:string
}

// AJOUTÉ : une couleur par statut (classes Tailwind)
const statusColor: Record<Doc["status"], string> = {
    pending: "bg-gray-500",
    processing: "bg-orange-500",
    ready: "bg-green-600",
    failed: "bg-red-600",
}

// CORRIGÉ : "Document" est déjà un nom du navigateur (la page HTML) → DocumentsPage
export default function DocumentsPage(){
    const[docs, setDocs] = useState<Doc[]>([])
    const[file, setFile] = useState<File | null>(null)
    const[uploading,setUploading] = useState(false)   
    const[error, setError] = useState("")
    const router = useRouter()

    async function loadDocs(){
        try {   
            const data = await apiFetch("/documents");
            setDocs(data)
        } catch (err) {
            setError((err as Error).message)
        }
    }

   useEffect(()=>{
        if(!localStorage.getItem("token")){
            router.push("/login")
            return   
        }
        
        apiFetch("/documents")
            .then(setDocs)
            .catch((err) => setError(err.message))
    }, [router] )

    const isProcessing = docs.some(d => d.status === "pending" || d.status === "processing")

    useEffect(()=>{
        if(!isProcessing) return
        const id = setInterval(loadDocs, 3000)
        return () => clearInterval(id)   
    }, [isProcessing])

    // 3. Envoi du PDF
    async function handleUpload(e:React.FormEvent<HTMLFormElement>){
        e.preventDefault();
        if(!file) return
        const form = e.currentTarget   

        setError("")
        setUploading(true)
        try {
            const formdata = new FormData()
            formdata.append("file", file)   
            
            await apiFetch("/documents", {method: "POST", body: formdata})
            setFile(null)
            form.reset()      
            await loadDocs() 
        } catch (err) {
            setError((err as Error).message)
        } finally {
            setUploading(false)
        }
    }

    function logout(){
        localStorage.removeItem("token")
        router.push("/login")
    }

    return (
        <main className="mx-auto flex w-full max-w-2xl flex-col gap-6 p-4">
            <div className="flex items-center justify-between">
                <h1 className="text-xl font-semibold">Mes documents</h1>
                <button onClick={logout} className="text-sm text-red-400 hover:underline">
                    Se déconnecter
                </button>
            </div>

            <form onSubmit={handleUpload} className="flex flex-wrap items-center gap-3">
                <input
                    type="file"
                    accept=".pdf"
                    onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                    className="text-sm"
                />
                <button
                    type="submit"
                    disabled={!file || uploading}
                    className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
                >
                    {uploading ? "Envoi..." : "Envoyer"}
                </button>
            </form>

            {error && <p className="text-xs text-red-400">{error}</p>}

            {docs.length === 0 ? (
                <p className="text-sm text-gray-400">Aucun document pour l&apos;instant.</p>
            ) : (
                <ul className="flex flex-col gap-2">
                    {docs.map(d => (
                        <li key={d.id} className="flex items-center justify-between gap-3 rounded-lg border border-gray-700 p-3">
                            <div className="min-w-0">
                                <p className="truncate text-sm font-medium">{d.filename}</p>
                                <p className="text-xs text-gray-400">
                                    <span className={`rounded px-2 py-0.5 text-white ${statusColor[d.status]}`}>{d.status}</span>
                                    {d.status === "ready" && <> · {d.chunk_count} chunks</>}
                                </p>
                            </div>
                            {d.status === "ready" && (
                                <Link href={`/documents/${d.id}`} className="text-sm text-blue-500 hover:underline">
                                    Ouvrir
                                </Link>
                            )}
                        </li>
                    ))}
                </ul>
            )}
        </main>
    )
}
