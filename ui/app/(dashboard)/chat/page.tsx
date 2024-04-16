import { Metadata } from "next"
import { Separator } from "@/components/ui/separator"
import ChatBoard from "@/app/(dashboard)/chat/components/chat-board"

export const metadata: Metadata = {
  title: "Chat",
  description: "The OpenAI Playground built using the components.",
}

export default function Chat() {

  return (
    <div className="hidden h-full flex-col md:flex">
      <div className="container flex flex-col items-start justify-between space-y-2 py-4 sm:flex-row sm:items-center sm:space-y-0 md:h-16">
        <h2 className="text-lg font-semibold">Chat</h2>
      </div>
      <Separator />
      <ChatBoard />
    </div>
  )
}