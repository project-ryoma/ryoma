import { Metadata } from "next"
import { Separator } from "@/components/ui/separator"
import { Tabs } from "@/components/ui/tabs"
import { CodeViewer } from "./components/code-viewer"

import { PresetActions } from "./components/preset-actions"
import { PresetSave } from "./components/preset-save"
import { PresetSelector } from "./components/preset-selector"

import { presets } from "./data/presets"
import ChatBoard from "@/app/(dashboard)/chat/components/chat-board"
import Image from "next/image"

export const metadata: Metadata = {
  title: "Chat",
  description: "The OpenAI Playground built using the components.",
}

export default function Chat() {

  return (
    <>
      <div className="md:hidden">
        <Image
          src="/examples/playground-light.png"
          width={1280}
          height={916}
          alt="Playground"
          className="block dark:hidden"
        />
        <Image
          src="/examples/playground-dark.png"
          width={1280}
          height={916}
          alt="Playground"
          className="hidden dark:block"
        />
      </div>
      <div className="hidden h-full flex-col md:flex">
        <div className="container flex flex-col items-start justify-between space-y-2 py-4 sm:flex-row sm:items-center sm:space-y-0 md:h-16">
          <h2 className="text-lg font-semibold">Chat</h2>
          <div className="ml-auto flex w-full space-x-2 sm:justify-end">
            <PresetSelector presets={presets} />
            <PresetSave />
            <div className="hidden space-x-2 md:flex">
              <CodeViewer />
            </div>
            <PresetActions />
          </div>
        </div>
        <Separator />
        <Tabs defaultValue="complete" className="flex-1">
          <ChatBoard />
        </Tabs>
      </div>
    </>
  )
}