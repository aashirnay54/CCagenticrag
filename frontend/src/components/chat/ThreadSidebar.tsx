import { Button } from '../ui/button'
import { ScrollArea } from '../ui/scroll-area'
import type { Thread } from '../../types/chat'

interface ThreadSidebarProps {
  threads: Thread[]
  activeThreadId: string | null
  onSelectThread: (id: string) => void
  onNewThread: () => void
  userEmail: string
  onSignOut: () => void
}

export function ThreadSidebar({
  threads,
  activeThreadId,
  onSelectThread,
  onNewThread,
  userEmail,
  onSignOut,
}: ThreadSidebarProps) {
  return (
    <div className="flex w-64 flex-none flex-col bg-muted/40 border-r h-full">
      <div className="p-3 border-b">
        <Button onClick={onNewThread} className="w-full" variant="outline" size="sm">
          + New Thread
        </Button>
      </div>

      <ScrollArea className="flex-1">
        {threads.length === 0 ? (
          <p className="p-4 text-sm text-muted-foreground">No threads yet</p>
        ) : (
          <div className="flex flex-col gap-1 p-2">
            {threads.map((thread) => (
              <button
                key={thread.id}
                onClick={() => onSelectThread(thread.id)}
                className={`w-full rounded-md px-3 py-2 text-left text-sm truncate transition-colors hover:bg-muted ${
                  activeThreadId === thread.id ? 'bg-muted font-medium' : 'text-muted-foreground'
                }`}
              >
                {thread.title}
              </button>
            ))}
          </div>
        )}
      </ScrollArea>

      <div className="border-t p-3 flex flex-col gap-2">
        <p className="text-xs text-muted-foreground truncate">{userEmail}</p>
        <Button onClick={onSignOut} variant="ghost" size="sm" className="w-full justify-start">
          Sign out
        </Button>
      </div>
    </div>
  )
}
