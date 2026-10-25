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
     
    return (
       <div className="flex flex-col gap-3">
        {messages.map((m, i)=>(

            <p key={i} className={`${m.owner==="user"  ? "self-end bg-blue-700 " : "self-start whitespace-pre-wrap bg-gray-600"} ${m.chunks_used?.map((c)=>(<p>{c}</p>)).join(", ")}` }>{m.content}</p>
        ))}
        {loading && <p>Réflexion......</p>}
        <form onSubmit={handleSubmit}>
             <input type="text" onChange={(e)=> setQuestion(e.target.value)} value={question} placeholder="Entrer votre Question"/>
             <button type="submit" disabled={loading}>Envoiyer</button>
        </form>
       
       </div>
    )
}