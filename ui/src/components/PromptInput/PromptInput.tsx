import { useEffect, useState, useCallback, useRef } from 'react';
import axios from 'axios';
import { Hint } from 'react-autocomplete-hint';
import './PromptInput.css';

interface PromptInputProps {
  prompt: string;
  onSubmit: () => void;
  updatePrompt: (prompt: string) => void;
}

const PromptInput: React.FC<PromptInputProps> = ({ prompt, onSubmit, updatePrompt }) => {
  const [options, setOptions] = useState<Array<{ id: number, label: string }>>([]);
  const timeoutIdRef = useRef<number | null>(null);  // Using a ref instead of state


  const checkKeyPress = useCallback((e: KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      if (e.ctrlKey || e.shiftKey) {
        document.execCommand('insertHTML', false, '<br/><br/>');
      } else {
        onSubmit();
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [prompt]);

  const fetchAutocompleteSuggestions = useCallback(async () => {
    try {
      const response = await axios.post('/autocomplete', {
        text: prompt
      });
      if (response.data && response.data.suggestions) {
        setOptions(response.data.suggestions.map((suggestion: string, index: number) => ({
          id: index,
          label: suggestion
        })));
      }
    } catch (error) {
      console.error('Error fetching autocomplete suggestions:', error);
    }
  }, [prompt]);

  useEffect(() => {
    if (prompt.length >= 3) {  // Only fetch suggestions when the user has typed at least 3 characters
      if (timeoutIdRef.current !== null) {
        clearTimeout(timeoutIdRef.current);  // clear the previous timeout if there is one
      }
      const id = window.setTimeout(() => {
        fetchAutocompleteSuggestions();  // fetch suggestions after 1 second
      }, 500);
      timeoutIdRef.current = id;
    }
    return () => {
      if (timeoutIdRef.current !== null) {
        clearTimeout(timeoutIdRef.current);  // clear the timeout when component is unmounted or re-rendered
      }
    };
  }, [prompt, fetchAutocompleteSuggestions]);

  useEffect(() => {
    window.addEventListener("keydown", checkKeyPress);
    return () => {
      window.removeEventListener("keydown", checkKeyPress);
    };
  }, [checkKeyPress]);
  
  return (
    <Hint options={options} allowTabFill={true}>
    <input
        value={prompt}
        id='prompt-input'
        onChange={e => updatePrompt(e.target.value)} />
    </Hint>
  );
};

export default PromptInput;
