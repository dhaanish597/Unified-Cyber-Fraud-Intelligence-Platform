import React, { useState } from 'react';
import { MessageSquare, Users, Pin, Send, UserCheck, Clock } from 'lucide-react';

export default function AnalystCollaboration({ caseId }) {
  const [comments, setComments] = useState([
    { author: 'Analyst_04 (Tier-3)', time: '10:01 IST', text: '@Analyst_02 Please double-check destination account ACC_MULE_NEW against cluster_alpha ring records.', pinned: true },
    { author: 'Analyst_02 (Tier-2)', time: '10:03 IST', text: 'Confirmed ring match. Shared device ID dev_9999 observed across 6 beneficiary accounts.', pinned: false }
  ]);
  const [newComment, setNewComment] = useState('');

  const handlePostComment = () => {
    if (!newComment.trim()) return;
    setComments(prev => [...prev, { author: 'Analyst_04 (Tier-3)', time: new Date().toLocaleTimeString(), text: newComment, pinned: false }]);
    setNewComment('');
  };

  return (
    <div className="bg-soc-panel border border-soc-border rounded-xl p-4 shadow-lg select-none font-mono text-xs">
      <div className="flex items-center justify-between border-b border-soc-border pb-3 mb-3">
        <div className="flex items-center gap-2">
          <Users className="w-5 h-5 text-soc-primary" />
          <div>
            <h3 className="font-bold text-soc-text text-xs uppercase tracking-wider">
              Analyst SOC Collaboration Suite
            </h3>
            <span className="text-[10px] text-soc-muted">
              Team Case Notes, @Mentions, Evidence Pinning & Escalation Log
            </span>
          </div>
        </div>
        <span className="text-[10px] px-2 py-0.5 rounded bg-soc-surface text-soc-muted border border-soc-border">
          2 Analysts Active
        </span>
      </div>

      {/* Comment Feed */}
      <div className="space-y-2 mb-3 max-h-[160px] overflow-y-auto pr-1">
        {comments.map((c, idx) => (
          <div key={idx} className="p-2.5 bg-soc-surface border border-soc-border rounded-lg space-y-1">
            <div className="flex justify-between items-center text-[10px]">
              <span className="font-bold text-soc-primary">{c.author}</span>
              <span className="text-soc-dim">{c.time}</span>
            </div>
            <p className="text-[11px] text-soc-text">{c.text}</p>
          </div>
        ))}
      </div>

      {/* Post Comment Bar */}
      <div className="flex items-center gap-2">
        <input
          type="text"
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder="Add investigation note or @mention analyst..."
          className="flex-1 bg-soc-bg border border-soc-border rounded px-3 py-1.5 text-xs text-soc-text placeholder-soc-dim focus:outline-none focus:border-soc-primary font-mono"
        />
        <button
          onClick={handlePostComment}
          className="px-3 py-1.5 bg-soc-primary hover:bg-blue-600 text-white rounded font-bold flex items-center gap-1 transition-colors shadow"
        >
          <Send className="w-3.5 h-3.5" />
          <span>Post</span>
        </button>
      </div>
    </div>
  );
}
