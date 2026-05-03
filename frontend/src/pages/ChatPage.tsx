import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'
import { useAuth } from '../contexts/AuthContext'
import { ThreadSidebar } from '../components/chat/ThreadSidebar'
import { MessageList } from '../components/chat/MessageList'
import { MessageInput } from '../components/chat/MessageInput'
import type { Thread, Message, StreamingMessage } from '../types/chat'

export function ChatPage() {
  const { user, signOut } = useAuth()
  const [threads, setThreads] = useState<Thread[]>([])
  const [activeThreadId, setActiveThreadId] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [streamingMessage, setStreamingMessage] = useState<StreamingMessage | null>(null)
  const [isSending, setIsSending] = useState(false)
  const [isLoadingMessages, setIsLoadingMessages] = useState(false)

  useEffect(() => {
    fetchThreads()
  }, [])

  useEffect(() => {
    if (activeThreadId) fetchMessages(activeThreadId)
    else setMessages([])
  }, [activeThreadId])

  const fetchThreads = async () => {
    const { data } = await supabase
      .from('threads')
      .select('*')
      .order('updated_at', { ascending: false })
    if (data) setThreads(data)
  }

  const fetchMessages = async (threadId: string) => {
    setIsLoadingMessages(true)
    const { data } = await supabase
      .from('messages')
      .select('*')
      .eq('thread_id', threadId)
      .order('created_at', { ascending: true })
    if (data) setMessages(data)
    setIsLoadingMessages(false)
  }

  const handleNewThread = () => {
    setActiveThreadId(null)
    setMessages([])
  }

  const handleSelectThread = (id: string) => {
    setActiveThreadId(id)
  }

  const handleSend = async (content: string) => {
    const threadIdBeforeSend = activeThreadId

    if (threadIdBeforeSend) {
      const optimisticMessage: Message = {
        id: crypto.randomUUID(),
        thread_id: threadIdBeforeSend,
        role: 'user',
        content,
        created_at: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, optimisticMessage])
    }

    setIsSending(true)
    setStreamingMessage({ role: 'assistant', content: '', isStreaming: true })

    const token = (await supabase.auth.getSession()).data.session?.access_token

    const response = await fetch(`${import.meta.env.VITE_API_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ thread_id: activeThreadId, message: content }),
    })

    const reader = response.body!.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() ?? ''
      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        const payload = JSON.parse(line.slice(6))
        if (payload.type === 'chunk') {
          setStreamingMessage((prev) =>
            prev ? { ...prev, content: prev.content + payload.content } : null
          )
        } else if (payload.type === 'done') {
          const resolvedThreadId: string = payload.thread_id
          setStreamingMessage(null)
          setIsSending(false)
          if (!threadIdBeforeSend) {
            setActiveThreadId(resolvedThreadId)
            await fetchThreads()
          }
          await fetchMessages(resolvedThreadId)
        }
      }
    }
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <ThreadSidebar
        threads={threads}
        activeThreadId={activeThreadId}
        onSelectThread={handleSelectThread}
        onNewThread={handleNewThread}
        userEmail={user?.email ?? ''}
        onSignOut={signOut}
      />
      <div className="flex flex-1 flex-col overflow-hidden">
        <MessageList
          messages={messages}
          streamingMessage={streamingMessage}
          isLoading={isLoadingMessages}
        />
        <MessageInput onSend={handleSend} disabled={isSending} />
      </div>
    </div>
  )
}
