# Voyager AI - Frontend

The frontend for Voyager AI, built with Next.js 14, TypeScript, and Tailwind CSS.

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript 5.x
- **Styling**: Tailwind CSS 3.x
- **UI Components**: shadcn/ui (Radix UI primitives)
- **Icons**: Lucide React
- **State Management**: React Context API + useReducer
- **Theme**: next-themes (dark mode support)
- **Testing**: Vitest + React Testing Library
- **Code Quality**: ESLint + Prettier

## Getting Started

### Prerequisites

- Node.js 18.x or higher
- npm (comes with Node.js)

### Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Environment Variables

Create a `.env.local` file in the frontend directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Project Structure

```
frontend/
├── app/                     # Next.js App Router
│   ├── chat/               # Chat page
│   ├── globals.css         # Global styles
│   ├── layout.tsx          # Root layout
│   └── page.tsx            # Home page (redirects to /chat)
│
├── components/
│   ├── chat/               # Chat-related components
│   │   ├── ChatInput.tsx           # Message input with send/stop
│   │   ├── ChatMessages.tsx        # Message list container
│   │   ├── MessageBubble.tsx       # Individual message bubble
│   │   ├── MarkdownRenderer.tsx    # Markdown processor
│   │   └── tool-cards/             # Tool result UI components
│   │       ├── FlightCard.tsx
│   │       ├── HotelCard.tsx
│   │       ├── WeatherCard.tsx
│   │       └── ToolResultCard.tsx  # Polymorphic dispatcher
│   │
│   ├── sidebar/            # Sidebar components
│   │   ├── Sidebar.tsx             # Main sidebar
│   │   ├── ConversationList.tsx    # Conversation history
│   │   └── ThemeToggle.tsx         # Dark mode toggle
│   │
│   └── ui/                 # shadcn/ui base components
│       ├── button.tsx
│       ├── card.tsx
│       ├── textarea.tsx
│       └── ...
│
├── contexts/
│   ├── ConversationsContext.tsx    # Conversation state management
│   └── ThemeProvider.tsx           # Theme provider (re-export)
│
├── hooks/
│   └── useChatStream.ts            # SSE streaming hook
│
├── lib/
│   ├── api/
│   │   ├── client.ts               # REST API client
│   │   └── chat.ts                 # SSE stream parser
│   ├── format.ts                   # Formatting utilities
│   └── utils.ts                    # cn() helper + misc
│
├── tests/                  # Vitest tests
│   ├── components/
│   ├── hooks/
│   ├── lib/
│   └── chat/
│
└── types/
    └── index.ts            # TypeScript type definitions
```

## Key Features

### 1. Server-Sent Events (SSE) Streaming

The `useChatStream` hook handles real-time streaming responses from the backend:

```typescript
const {
  messages,
  streamingContent,
  isStreaming,
  sendMessage,
  stopStreaming,
} = useChatStream(conversationId);
```

**Features**:
- Real-time token streaming
- Tool result updates during streaming
- Abort/stop mid-stream
- Error handling with retry logic

### 2. Conversation Management

The `ConversationsContext` provides global conversation state:

```typescript
const {
  conversations,
  activeConversationId,
  createConversation,
  updateConversation,
  deleteConversation,
  setActiveConversation,
} = useConversations();
```

### 3. Tool Result Cards

Polymorphic tool result rendering based on type:

```typescript
<ToolResultCard type="flight" data={flightData} />
<ToolResultCard type="hotel" data={hotelData} />
<ToolResultCard type="weather" data={weatherData} />
```

Automatically renders the correct card component based on the `type` field.

### 4. Dark Mode

System-aware dark mode with manual toggle:

```typescript
import { ThemeToggle } from "@/components/sidebar/ThemeToggle";

<ThemeToggle />
```

Uses `next-themes` to prevent FOUC (Flash of Unstyled Content).

### 5. Markdown Rendering

Rich text formatting in assistant messages:

- **Bold**, *italic*, `code`
- Links, lists, headings
- Code blocks with syntax highlighting (future)

## Available Scripts

```bash
# Development
npm run dev          # Start dev server (port 3000)

# Building
npm run build        # Production build
npm start            # Start production server

# Code Quality
npm run lint         # Run ESLint
npm run format       # Run Prettier

# Testing
npm test             # Run Vitest tests
npm test -- --ui     # Run with UI
npm test -- --coverage  # Run with coverage report
```

## Testing

Tests are written using Vitest and React Testing Library.

### Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run specific test file
npm test ChatInput.test.tsx

# Generate coverage report
npm test -- --coverage
```

### Test Organization

```
tests/
├── components/              # Component tests
│   ├── ChatInput.test.tsx
│   └── MessageBubble.test.tsx
├── hooks/                   # Hook tests
│   └── useChatStream.test.ts
├── lib/                     # Utility tests
│   ├── api/
│   │   └── client.test.ts
│   └── format.test.ts
└── chat/
    └── tool-cards/          # Tool card tests
        └── FlightCard.test.tsx
```

### Example Test

```typescript
import { render, screen } from "@testing-library/react";
import { ChatInput } from "@/components/chat/ChatInput";

it("renders textarea and send button", () => {
  render(<ChatInput onSubmit={vi.fn()} isStreaming={false} />);

  expect(screen.getByLabelText("Message input")).toBeInTheDocument();
  expect(screen.getByLabelText("Send message")).toBeInTheDocument();
});
```

## Styling

### Tailwind CSS

The project uses Tailwind CSS with a custom configuration:

```typescript
// tailwind.config.ts
export default {
  darkMode: ["class"],
  theme: {
    extend: {
      colors: {
        flight: "hsl(var(--flight))",
        hotel: "hsl(var(--hotel))",
        // ...
      },
    },
  },
};
```

### CSS Variables

Theme colors are defined in `app/globals.css`:

```css
:root {
  --flight: 221 83% 53%;      /* Blue for flights */
  --hotel: 142 71% 45%;       /* Green for hotels */
  --weather: 43 74% 49%;      /* Yellow for weather */
  /* ... */
}
```

### shadcn/ui Components

Components from shadcn/ui are copied into `components/ui/` for customization:

- No external dependency on shadcn/ui package
- Full control over styling and behavior
- Easy to modify component internals

## API Integration

### REST API Client

```typescript
import { api } from "@/lib/api/client";

// List conversations
const conversations = await api.getConversations();

// Create conversation
const newConv = await api.createConversation("Trip to Paris");

// Get messages
const messages = await api.getMessages(conversationId);
```

### SSE Streaming

```typescript
import { streamChat } from "@/lib/api/chat";

await streamChat(
  conversationId,
  "Find me flights to Tokyo",
  {
    onToken: (token) => console.log(token),
    onToolResult: (result) => console.log(result),
    onComplete: (content, toolResults) => console.log("Done!"),
    onError: (error) => console.error(error),
  },
  abortSignal
);
```

## TypeScript Types

All types are defined in `types/index.ts`:

```typescript
export interface Message {
  id?: string;
  role: "user" | "assistant";
  content: string;
  toolResults?: ToolResult[];
  timestamp: string;
}

export interface Conversation {
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
}

export interface ToolResult {
  type: string;
  data: ToolResultData;
}
```

## Performance

### Current Bundle Sizes

- **/chat**: 114 KB First Load JS
- Total First Load JS: 114 KB (under 150 KB target)

### Optimizations

- React Server Components (where applicable)
- Dynamic imports for large components
- CSS-only animations (no Framer Motion)
- No external icon fonts (using Lucide React)

## Common Tasks

### Adding a New Tool Card

1. Create component in `components/chat/tool-cards/`:

```typescript
export function NewToolCard({ data }: { data: ToolResultData }) {
  const typedData = data as NewToolResult;
  return <Card>...</Card>;
}
```

2. Update `ToolResultCard.tsx`:

```typescript
case "newtool":
  return <NewToolCard data={data} />;
```

3. Add type to `types/index.ts`:

```typescript
export interface NewToolResult {
  // ...fields
}
```

### Adding a New API Endpoint

1. Add function to `lib/api/client.ts`:

```typescript
async newEndpoint(param: string): Promise<Response> {
  const res = await fetch(`${this.baseUrl}/api/new-endpoint`, {
    method: "POST",
    body: JSON.stringify({ param }),
  });
  return res.json();
}
```

2. Use in components:

```typescript
const result = await api.newEndpoint("value");
```

## Troubleshooting

### Port Already in Use

```bash
# Kill process on port 3000
npx kill-port 3000

# Or use a different port
npm run dev -- -p 3001
```

### Module Not Found

```bash
# Clear Next.js cache
rm -rf .next
npm run dev
```

### TypeScript Errors

```bash
# Regenerate types
npm run build
```

## Resources

- [Next.js Docs](https://nextjs.org/docs)
- [shadcn/ui](https://ui.shadcn.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Vitest](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)

---

**Frontend built with Next.js 14 and TypeScript**
