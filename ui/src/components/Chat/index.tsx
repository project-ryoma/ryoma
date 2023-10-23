import {useState} from 'react';
import axios from "axios";
import Navbar from "../Navbar";
import PromptInput from "../PromptInput/PromptInput";
import './chat.css';
import {ResponseInterface} from "../PromptResponseList/response-interface";
import PromptResponseList from "../PromptResponseList/PromptResponseList";
import Visuals from "../Visuals";

type ModelValueType = 'gpt' | 'llama' | 'fine-tuned-llama';
const Chat = () => {

  const [responseList, setResponseList] = useState<ResponseInterface[]>([]);
  const [prompt, setPrompt] = useState<string>('');
  const [promptToRetry, setPromptToRetry] = useState<string | null>(null);
  const [uniqueIdToRetry, setUniqueIdToRetry] = useState<string | null>(null);
  const [modelValue, setModelValue] = useState<ModelValueType>('gpt');
  const [isLoading, setIsLoading] = useState(false);
  const [reportCreated, setReportCreated] = useState(false);
  const [reportConfig, setReportConfig] = useState(null);
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


  const addResponse = (selfFlag: boolean, response?: string) => {
    const uid = generateUniqueId()
    setResponseList(prevResponses => [
      ...prevResponses,
      {
        id: uid,
        response,
        selfFlag
      },
    ]);
    return uid;
  }

  const updateResponse = (uid: string, updatedObject: Record<string, unknown>) => {
    setResponseList(prevResponses => {
      const updatedList = [...prevResponses]
      const index = prevResponses.findIndex((response) => response.id === uid);
      if (index > -1) {
        updatedList[index] = {
          ...updatedList[index],
          ...updatedObject
        }
      }
      return updatedList;
    });
  }

  const regenerateResponse = async () => {
    await getGPTResult(promptToRetry, uniqueIdToRetry);
  }

  const getGPTResult = async (_promptToRetry?: string | null, _uniqueIdToRetry?: string | null) => {
    // Get the prompt input
    const _prompt = _promptToRetry ?? htmlToText(prompt);

    // If a response is already being generated or the prompt is empty, return
    if (isLoading || !_prompt) {
      return;
    }

    setIsLoading(true);

    // Clear the prompt input
    setPrompt('');

    let uniqueId: string;
    if (_uniqueIdToRetry) {
      uniqueId = _uniqueIdToRetry;
    } else {
      // Add the self prompt to the response list
      addResponse(true, _prompt);
      uniqueId = addResponse(false);
      await delay(50);
      addLoader(uniqueId);
    }

    try {
      // Send a POST request to the API with the prompt in the request body
      const response = await axios.post('chatv2', {
        prompt: _prompt,
        model: modelValue
      });

      updateResponse(uniqueId, {
        response: response.data.trim(),
      });

      setPromptToRetry(null);
      setUniqueIdToRetry(null);

      // Check if the response contains report information
      if (response.data.indexOf("I have created a report for you") > -1) {

        // Assuming response.data.report contains embedUrl and embedReportId
        setReportConfig(response.data);
        setReportCreated(true);
      }

    } catch (err) {
      setPromptToRetry(_prompt);
      setUniqueIdToRetry(uniqueId);
      updateResponse(uniqueId, {
        // @ts-ignore
        response: `Error: ${err.message}`,
        error: true
      });
    } finally {
      // Clear the loader interval
      clearInterval(loadInterval);
      setIsLoading(false);
    }
  }

  return (
    <div className="Chat">
      <Navbar />
      <div id="response-list">
        <PromptResponseList responseList={responseList} key="response-list"/>
        
      {/* Visuals */}
      {reportCreated && reportConfig &&
        (
          <div id="visual-container">
            <Visuals />
          </div>
        )
      }

      </div>
      { uniqueIdToRetry &&
        (<div id="regenerate-button-container">
          <button id="regenerate-response-button" className={isLoading ? 'loading' : ''} onClick={() => regenerateResponse()}>
            Regenerate Response
          </button>
        </div>
        )
      }

      <div id="model-select-container">
        <label htmlFor="model-select">Select model:</label>
        <select id="model-select" value={modelValue} onChange={(event) => setModelValue(event.target.value as ModelValueType)}>
          <option value="gpt">GPT-3 (Understand and generate natural language )</option>
          <option value="llama">llama (Understand and generate natural language)</option>
          <option value="fine-tuned-llama">fine-tuned-llama (Understand and generate natural language)</option>
        </select>
      </div>
      <div id="input-container">
        <PromptInput
          prompt={prompt}
          onSubmit={() => getGPTResult()}
          key="prompt-input"
          updatePrompt={(prompt) => setPrompt(prompt)}
        />
        <button id="submit-button" className={isLoading ? 'loading' : ''} onClick={() => getGPTResult()}></button>
      </div>

    </div>
  );
}

export default Chat;
