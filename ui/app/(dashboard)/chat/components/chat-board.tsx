"use client";
import * as React from "react"
import ChatForm from "@/components/forms/chat-form"
import ChatHistory from "./chat-history";
import { MessageInterface } from "./message-interface";
import { MaxLengthSelector } from "./maxlength-selector"
import { ModelSelector } from "./model-selector"
import { DataSourceSelector } from "./datasource-selector"
import { TemperatureSelector } from "./temperature-selector"
import { TopPSelector } from "./top-p-selector"
import { useState } from "react";
import { Model, models, types } from "../data/models"
import { DataSource, dataSources, types as datatype } from "../../datasource/data/datasource"
import * as z from "zod";
import axios from "axios";
import ToolForm from "@/components/forms/tool-form";
import { set } from "date-fns";

const formSchema = z.object({
  question: z.string(),
});

const toolFormSchema = z.object({
  name: z.string(),
  arguments: z.record(z.string()),
});


export interface ToolInterface {
  id: string;
  name: string;
  arguments: Record<string, string>;
}

function ChatBoard() {
  const [messages, setMessages] = useState<MessageInterface[]>([]);
  const [prompt, setPrompt] = useState<string>('');
  const [tool, setTool] = useState<ToolInterface | null>(null);
  const [selectedModel, setSelectedModel] = React.useState<Model>(models[0])
  const [peekedModel, setPeekedModel] =  React.useState<Model>(models[0])
  const [temperature, setTemperature] = React.useState([0.56])
  const [topP, setTopP] = React.useState([0.9])
  const [maxLength, setMaxLength] = React.useState([256])
  const [selectedDataSource, setSelectedDataSource] = React.useState<DataSource>(dataSources[0])
  const [peekedDataSource, setPeekedDataSource] = React.useState<DataSource>(dataSources[0])
  const [promptToRetry, setPromptToRetry] = useState<string | null>(null);
  const [uniqueIdToRetry, setUniqueIdToRetry] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  let loadInterval: number | undefined;


  const generateUniqueId = () => {
    const timestamp = Date.now();
    const randomNumber = Math.random();
    const hexadecimalString = randomNumber.toString(16);

    return `id-${timestamp}-${hexadecimalString}`;
  }

  const htmlToText = (html: string) => {
    const temp = document.createElement('div');
    temp.innerHTML = html;
    return temp.textContent;
  }

  const delay = (ms: number) => {
    return new Promise( resolve => setTimeout(resolve, ms) );
  }

  const addLoader = (uid: string) => {
    const element = document.getElementById(uid) as HTMLElement;

    element.textContent = ''

    // @ts-ignore
    loadInterval = setInterval(() => {
      // Update the text content of the loading indicator
      element.textContent += '.';

      // If the loading indicator has reached three dots, reset it
      if (element.textContent === '....') {
        element.textContent = '';
      }
    }, 300);
  }

  const addMessage = (selfFlag: boolean, message?: string) => {
    const uid = generateUniqueId()
    setMessages(prevMessages => [
      ...prevMessages,
      {
        id: uid,
        text: message,
        selfFlag,
      },
    ]);
    return uid;
  }

  const updateMessage = (uid: string, updatedObject: Record<string, unknown>) => {
    setMessages(prevMessages => {
      const updatedMessages = [...prevMessages]
      const index = prevMessages.findIndex((message) => message.id === uid);
      if (index > -1) {
        updatedMessages[index] = {
          ...updatedMessages[index],
          ...updatedObject,
        }
      }
      return updatedMessages;
    });
  }

  const onSubmit = async (values: z.infer<typeof formSchema>, _uniqueIdToRetry?: string | null) =>{
    const { question } = values;

    // Get the prompt input
    const _prompt = question ?? htmlToText(prompt);

    // If a response is already being generated or the prompt is empty, return
    if (loading || !_prompt) {
      return;
    }

    setLoading(true);

    // Clear the prompt input
    setPrompt('');

    let uniqueId: string;
    if (_uniqueIdToRetry) {
      uniqueId = _uniqueIdToRetry;
    } else {
      // Add the self prompt to the response list
      addMessage(true, _prompt);
      uniqueId = addMessage(false);
      await delay(50);
      addLoader(uniqueId);
    }

    try {
      // Send a POST request to the API with the prompt in the request body
      const response = await axios.post('/api/chat', {
        prompt: _prompt,
        model: selectedModel.id,
        agent: "sql",
        temperature: temperature[0],
        top_p: topP[0],
        max_length: maxLength[0],
        datasource: selectedDataSource.id,
      });

      updateMessage(uniqueId, {
        text: response.data.message.trim(),
      });

      if (response.data.additional_info && response.data.additional_info.type == "use_tool") {
        setTool(response.data.additional_info);
      }

      setPromptToRetry(null);
      setUniqueIdToRetry(null);

    } catch (err) {
      setPromptToRetry(_prompt);
      setUniqueIdToRetry(uniqueId);
      updateMessage(uniqueId, {
        // @ts-ignore
        text: `Error: ${err.message}`,
        error: true
      });
    } finally {
      // Clear the loader interval
      clearInterval(loadInterval);
      setLoading(false);
    }
  }

  const handleToolSubmit = async (values: z.infer<typeof toolFormSchema>) => {
    const { name, arguments: args } = values;


    let uniqueId: string;
    uniqueId = addMessage(false);
    await delay(50);

    const response = await axios.post('http://localhost:3001/api/v1/tools/run', {
      name,
      arguments: args,
    });
    
    updateMessage(uniqueId, {
      text: response.data.message.trim(),
    });

    if (response.data.additional_info && response.data.additional_info.type == "use_tool") {
      setTool(response.data.additional_info);
    }

    setPromptToRetry(null);
    setUniqueIdToRetry(null);
    
  }

  return (
    <div className="container h-full py-6">
      <div className="grid h-full items-stretch gap-6 md:grid-cols-[1fr_200px]">
        <div className="hidden flex-col space-y-4 sm:flex md:order-2">
          <div className="flex-col border p-2 rounded-md">
            <ModelSelector
              types={types}
              models={models}
              selectedModel={selectedModel}
              peekedModel={peekedModel}
              onSelectModel={(model) => {
                setSelectedModel(model);
              }}
              onPeekModel={(model) => {
                setPeekedModel(model);
              }}
            />
            <TemperatureSelector
              temperature={temperature}
              onTemperatureChange={(value) => {
                setTemperature(value);
              }}
            />
            <MaxLengthSelector
              maxLength={maxLength}
              onMaxLengthChange={(value) => {
                setMaxLength(value);
              }} 
            />
            <TopPSelector
              topP={topP}
              onTopPChange={(value) => {
                setTopP(value);
              }}
            />
          </div>
          <div className="flex-col border p-2 rounded-md">
            <DataSourceSelector
              types={datatype}
              dataSources={dataSources}
              selectedDataSource={selectedDataSource}
              peekedDataSource={peekedDataSource}
              onSelectDataSource={(dataSource) => {
                setSelectedDataSource(dataSource);
              }}
              onPeekDataSource={(dataSource) => {
                setPeekedDataSource(dataSource);
              }}
            />
          </div>
        </div>
        <div className="md:order-1">
          <div className="flex flex-1 flex-col h-full">
           <div className="flex-1 h-full hidden items-start justify-center gap-6 rounded-lg p-8 md:grid lg:grid-cols-2 xl:grid-cols-2">
             <div className="flex-1 overflow-auto lg:col-span-2 border rounded-md">
               <ChatHistory messages={messages} />
             </div>
             {tool && tool.name && tool.arguments && (
               <div className="h-full lg:col-span-1 rounded-md border bg-muted">
                 <ToolForm
                   tool={tool}
                   onConfirm={handleToolSubmit}
                   onCancel={() => {
                     setTool(null);
                   }}
                 />
               </div>
             )}
           </div>
           <div className="flex-initial p-4 bg-white border-t border-gray-200">
             <ChatForm onSubmit={onSubmit} loading={loading}  />
           </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ChatBoard;