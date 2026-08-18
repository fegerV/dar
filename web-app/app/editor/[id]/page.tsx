import { EditorScreen } from "@/components/editor"

export default function EditorPage({ params }: { params: { id: string } }) {
  return <EditorScreen generationId={params.id} />
}
