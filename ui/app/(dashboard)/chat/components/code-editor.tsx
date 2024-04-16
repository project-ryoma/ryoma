// create a code editor component by using the Monaco Editor

import React, { useEffect, useState } from 'react';
import MonacoEditor from 'react-monaco-editor';

interface CodeEditorProps {
  value: string;
  language: string;
  onChange: (value: string) => void;
}

export const CodeEditor: React.FC<CodeEditorProps> = ({ value, language, onChange }) => {
  const [editorValue, setEditorValue] = useState(value);

  useEffect(() => {
    setEditorValue(value);
  }, [value]);

  const handleEditorChange = (newValue: string) => {
    setEditorValue(newValue);
    onChange(newValue);
  };

  console.log(value);

  return (
    <MonacoEditor
      height="100px"
      language={language}
      theme="vs-dark"
      value={editorValue}
      onChange={handleEditorChange}
      options={
        {
          minimap: { enabled: false },
          automaticLayout: true,
          scrollBeyondLastLine: false,
          wordWrap: 'on',
          wrappingIndent: 'same',
          wrappingStrategy: 'advanced',
          wordWrapColumn: 80,
        }
      }
    />
  );
};