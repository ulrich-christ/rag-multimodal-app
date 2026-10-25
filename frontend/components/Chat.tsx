"use client"
import {useState} from "react"
import {apiFetch} from "@/lib/api"
type ChatProps = {document_id:number}
type Message = {
    owner:"user" | "assistant",
    content:string,
    search_question?:string,
    chunks_used?:number[]

}
export default function Chat({document_id}:ChatProps){
     const [messages, setMessages] = useState<Message[]>([])
     const [question, setQuestion] = useState("")
     const [loading, setLoading] = useState(false)
     const [error, setError] = useState("")
     async function handleSubmit(e:React.FormEvent) {
        e.preventDefault()
        const q = question.trim()
        if (!q) return

        setError("")
        setMessages((prev) => [...prev, {owner:"user", content:q}])
        setQuestion("")
        setLoading(true)

        try{
            const data = await apiFetch("/chat", {
                method:"POST",
                headers:{"Content-Type":"application/json"},
                body:JSON.stringify({document_id:document_id, question:q})
            })

            setMessages((prev) => [...prev, {
                owner:"assistant",
                content:data.answer,
                chunks_used:data.chunks_used
            }])

        }catch(err){
            setError((err as Error).message)
        }finally{
            setLoading(false)
        }
     }
         const inputClass = "w-full bg-gray-800 border border-gray-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"

    return (
       <div className="flex flex-col gap-3">
        {messages.map((m, i)=>(

            <p key={i} className={`${m.owner==="user"  ? "self-end bg-blue-700 whitespace-pre-wrap rounded-lg px-3 py-2 max-w-[80%] text-white" : "self-start whitespace-pre-wrap bg-gray-600 rounded-lg px-3 py-2 max-w-[80%] text-white"}` }>{m.content} {m.owner === "assistant" ? m.chunks_used?.map((c)=>(`#${c}`)).join(", ") :""}</p>
        ))}
        {loading && <p>Réflexion......</p>}
        {error && <p>{error}</p>
        }
        <form onSubmit={handleSubmit} className="flex gap-2">
             <input type="text" onChange={(e)=> setQuestion(e.target.value)} value={question} placeholder="Entrer votre Question"/>
             <button className={inputClass} type="submit" disabled={loading}>Envoiyer</button>
        </form>
       
       </div>
    )
}