import React, {FC, useEffect, useRef} from 'react';
import ChatGptImg from '../../img/chatgpt.png';
import MyImg from '../../img/me.png';
import ReactMarkdown from 'react-markdown';
import {ResponseInterface} from "./response-interface";
import hljs from 'highlight.js';
import './PromptResponseList.css';

interface PromptResponseListProps {
  responseList: ResponseInterface[];
}

const PromptResponseList: FC<PromptResponseListProps> = ({ responseList }) => {
  const responseListRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    hljs.highlightAll();
  })

  useEffect(() => {
    hljs.highlightAll();
  }, [responseList]);

  return (
    <div className="prompt-response-list" ref={responseListRef}>
      {responseList.map((responseData) => (
        <div className={"response-container " + (responseData.selfFlag ? 'my-question' : 'chatgpt-response')} key={responseData.id}>
          <img className="avatar-image" src={responseData.selfFlag ? MyImg : ChatGptImg} alt="avatar"/>
          <div className={(responseData.error ? 'error-response ' : '') + "prompt-content"} id={responseData.id}>
            { responseData.image &&
                <img src={responseData.image} className="ai-image" alt="generated ai"/>
            }
            { responseData.response &&
              <ReactMarkdown
                children={responseData.response ?? ''}
                components={{
                  code({className, children}) {
                    return(
                      <code className={className}>
                        {children}
                      </code>
                    )
                  }
                }}
              />
            }
          </div>
        </div>
      ))}
    </div>
  );
};

export default PromptResponseList;
