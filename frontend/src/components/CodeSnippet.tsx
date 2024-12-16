import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { materialDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface CodeSnippetProps {
  language: string;
  codeString: string;
}

export function CodeSnippet({ language, codeString }: CodeSnippetProps) {
  return (
    <SyntaxHighlighter language={language} style={materialDark} showLineNumbers>
      {codeString}
    </SyntaxHighlighter>
  );
}
