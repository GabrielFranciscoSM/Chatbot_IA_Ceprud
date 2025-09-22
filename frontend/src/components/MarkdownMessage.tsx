import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/atom-one-light.css'; // Better theme for code highlighting

interface MarkdownMessageProps {
  content: string;
  className?: string;
}

const MarkdownMessage: React.FC<MarkdownMessageProps> = ({ content, className = '' }) => {
  return (
    <div className={`markdown-content ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeHighlight]}
        components={{
        // Custom styling for different markdown elements
        p: ({ children }) => <p className="markdown-paragraph">{children}</p>,
        strong: ({ children }) => <strong className="markdown-bold">{children}</strong>,
        em: ({ children }) => <em className="markdown-italic">{children}</em>,
        code: ({ children, className }) => {
          const isInline = !className;
          return isInline ? (
            <code className="markdown-inline-code">{children}</code>
          ) : (
            <code className={className}>{children}</code>
          );
        },
        pre: ({ children }) => <pre className="markdown-code-block">{children}</pre>,
        ul: ({ children }) => <ul className="markdown-list">{children}</ul>,
        ol: ({ children }) => <ol className="markdown-list markdown-ordered-list">{children}</ol>,
        li: ({ children }) => <li className="markdown-list-item">{children}</li>,
        blockquote: ({ children }) => <blockquote className="markdown-blockquote">{children}</blockquote>,
        h1: ({ children }) => <h1 className="markdown-heading markdown-h1">{children}</h1>,
        h2: ({ children }) => <h2 className="markdown-heading markdown-h2">{children}</h2>,
        h3: ({ children }) => <h3 className="markdown-heading markdown-h3">{children}</h3>,
        h4: ({ children }) => <h4 className="markdown-heading markdown-h4">{children}</h4>,
        h5: ({ children }) => <h5 className="markdown-heading markdown-h5">{children}</h5>,
        h6: ({ children }) => <h6 className="markdown-heading markdown-h6">{children}</h6>,
        a: ({ href, children }) => (
          <a href={href} className="markdown-link" target="_blank" rel="noopener noreferrer">
            {children}
          </a>
        ),
        table: ({ children }) => <table className="markdown-table">{children}</table>,
        thead: ({ children }) => <thead className="markdown-table-head">{children}</thead>,
        tbody: ({ children }) => <tbody className="markdown-table-body">{children}</tbody>,
        tr: ({ children }) => <tr className="markdown-table-row">{children}</tr>,
        th: ({ children }) => <th className="markdown-table-header">{children}</th>,
        td: ({ children }) => <td className="markdown-table-cell">{children}</td>,        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

export default MarkdownMessage;
