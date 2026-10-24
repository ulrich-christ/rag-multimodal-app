"use client"
import {useParams, useRouter} from "next/navigation"
import {useState, useEffect, Suspense} from "react"
import {apiFetch} from "@/lib/api"
import Link from "next/link"
import DOMPurify from "dompurify";


type Doc = {
    id:number;
    filename:string;
    status:"pending" | "processing" | "ready" | "failed" ;
    chunk_count:number
    created_at:string
}

type Chunk = {
            chunk_index: number,
            page_number:number,
            types: string,
            has_summary: boolean,
            summary: string | null,
            raw_text: string,
            tables_html: string[],
            images_base64: string[]
}
export default function DocumentPage(){
    return (

        <Suspense fallback={<p>Chargement...</p>}>
            <DocumentPipeline />
        </Suspense>
    )
}

function DocumentPipeline(){
    const router = useRouter()
    const {id} = useParams<{id:string}>()
    const [doc, setDoc] = useState<Doc | null>(null)
    const [chunks, setChunks] = useState<Chunk []>([])
    const [error, setError] = useState("")
    const [activetab, setActiveTab] = useState<"pipeline" | "chat">("pipeline")


    useEffect(()=>{
        if(!localStorage.getItem("token")){
            router.push("/login")
            return
        }
        apiFetch(`/documents/${id}`)
            .then(setDoc)
            .catch((err) => setError(err.message))

        apiFetch(`/documents/${id}/chunks`)
            .then(setChunks)
            .catch((err) => setError(err.message))
    }, [id, router])
    if (error) return <p>{error}</p>
    if(!doc){
        return <p>Chargement...</p>
    }

  
    const nbChunks = chunks.length

    const nbResumes = chunks.filter((c) => c.has_summary).length

    
    const nbTableaux = chunks.reduce((total, c) => total + c.tables_html.length, 0)

   
    const nbImages = chunks.reduce((total, c) => total + c.images_base64.length, 0)
  console.log(chunks)

    return (
        <main className="mx-auto flex w-full max-w-4xl flex-col gap-6 p-4">
                {/* Lien retour en haut, puis le nom du fichier comme titre */}
                <Link href={"/documents"} className="text-sm text-blue-500 hover:underline">← Mes documents</Link>
                <h1 className="truncate text-xl font-semibold">{doc.filename}</h1>

                {/* Les 6 étapes du pipeline, dans l'ordre : de l'ingestion jusqu'au modèle */}
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    <div className="rounded-lg border border-gray-700 p-3 text-xs text-gray-400">
                        <p>1. Partition</p>
                        {/* Texte fixe : plus petit que les chiffres */}
                        <p className="mt-1 text-sm font-semibold text-white">unstructured · hi_res</p>
                    </div>
                    <div className="rounded-lg border border-gray-700 p-3 text-xs text-gray-400">
                        <p>2. Chunking</p>
                        {/* {} = on affiche la valeur de la variable */}
                        <p className="text-2xl font-semibold text-white">{nbChunks} chunks</p>
                    </div>
                    <div className="rounded-lg border border-gray-700 p-3 text-xs text-gray-400">
                        <p>3. Résumé IA</p>
                        <p className="text-2xl font-semibold text-white">{nbResumes} résumés</p>
                    </div>
                    <div className="rounded-lg border border-gray-700 p-3 text-xs text-gray-400">
                        <p>4. Tableaux & images</p>
                        <p className="text-2xl font-semibold text-white">{nbTableaux} · {nbImages}</p>
                        <p>tableaux · images</p>
                    </div>
                    <div className="rounded-lg border border-gray-700 p-3 text-xs text-gray-400">
                        <p>5. Embeddings</p>
                        <p className="mt-1 text-sm font-semibold text-white">text-embedding-3-small · pgvector</p>
                    </div>
                    <div className="rounded-lg border border-gray-700 p-3 text-xs text-gray-400">
                        <p>6. Retrieval → LLM</p>
                        <p className="mt-1 text-sm font-semibold text-white">3 chunks envoyés au modèle</p>
                    </div>
                </div>
                <div className="flex flex-col gap-3">
                    {chunks.map((c)=> (
                        <div key={c.chunk_index} className="flex flex-col gap-2 rounded-lg border border-gray-700 p-3">
                            <p className="font-semibold">Chunk #{c.chunk_index} · Page {c.page_number}</p>

                            <div className="flex flex-wrap items-center gap-2 text-xs text-gray-400">
                                Types :
                                {c.types.split(",").map((t)=>(
                                    <span key={t} className="rounded bg-blue-600 px-2 py-0.5 text-white">{t}</span>
                                ))}
                            </div>
                             <div className="flex flex-wrap items-center gap-2 text-xs text-gray-400">
                                
                                {c.images_base64.map((im, i)=>(
                                    <div key={i}>
                                        {/* Commentaire JSX : entre accolades. La ligne suivante coupe l'avertissement pour la balise juste en dessous */}
                                        {/* eslint-disable-next-line @next/next/no-img-element */}
                                        <img className="max-w-full" src={`data:image/jpeg;base64,${im}`} alt={`Figure du chunk ${c.chunk_index}`} />
                                    </div>
                                ))}
                            </div>

                              <div className="overflow-x-auto">
                                
                                {c.tables_html.map((t,i)=>(
                                    <div key={i}>
                                        <div  className= "pdf-table" dangerouslySetInnerHTML={{__html: DOMPurify.sanitize(t) }}></div>
                                    </div>
                                ))}
                            </div>

                            {c.summary && <p className="whitespace-pre-wrap text-sm">{c.summary}</p>}

                            <details>
                                <summary className="cursor-pointer text-sm text-gray-400">Texte brut</summary>
                                <p className="mt-2 whitespace-pre-wrap text-sm">{c.raw_text}</p>
                            </details>
                        </div>
                    ))}
                </div>
        </main>
      
      
    )
}