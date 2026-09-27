import { useMemo } from 'react'
import ReactFlow, { Background, Controls, MarkerType } from 'reactflow'
import 'reactflow/dist/style.css'

const COLUMN_WIDTH = 220
const ROW_HEIGHT = 90
const NODES_PER_ROW = 4

// The backend gives us { nodes: [{id,label,file,type}], edges: [{source,target}] }
// with no layout info, so lay them out in a simple grid — good enough for
// the small, filtered subgraphs this app shows (seed nodes + 1 hop).
function layout(rawNodes) {
  return rawNodes.map((n, i) => ({
    id: n.id,
    position: { x: (i % NODES_PER_ROW) * COLUMN_WIDTH, y: Math.floor(i / NODES_PER_ROW) * ROW_HEIGHT },
    data: { label: `${n.label || n.file.split('/').pop()}` },
    style: {
      background: n.type?.includes('class') ? '#2d1b4e' : '#1b2a4e',
      color: '#fff',
      border: '1px solid #7c3aed',
      borderRadius: 8,
      fontSize: 12,
      padding: 8,
      width: COLUMN_WIDTH - 30,
    },
  }))
}

function layoutEdges(rawEdges) {
  return rawEdges.map((e, i) => ({
    id: `e${i}-${e.source}-${e.target}`,
    source: e.source,
    target: e.target,
    animated: true,
    style: { stroke: '#7c3aed' },
    markerEnd: { type: MarkerType.ArrowClosed, color: '#7c3aed' },
  }))
}

export default function GraphView({ graph }) {
  const nodes = useMemo(() => layout(graph?.nodes || []), [graph])
  const edges = useMemo(() => layoutEdges(graph?.edges || []), [graph])

  if (!graph || nodes.length === 0) {
    return <div style={{ fontSize: 12, opacity: 0.6 }}>No call-graph relationships found for this answer's citations.</div>
  }

  return (
    <div style={{ height: 320, background: '#0a0a0f', borderRadius: 8 }}>
      <ReactFlow nodes={nodes} edges={edges} fitView nodesDraggable nodesConnectable={false} elementsSelectable={false}>
        <Background color="#25253a" gap={16} />
        <Controls showInteractive={false} />
      </ReactFlow>
      <div style={{ fontSize: 11, opacity: 0.5, padding: '4px 8px' }}>
        {nodes.length} functions, {edges.length} call relationships (name-matched, not scope-resolved)
      </div>
    </div>
  )
}
