import { Trophy, Medal } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useState } from 'react'

interface TeamLeaderboardProps {}

interface Team {
  id: string
  name: string
  description: string
  members: number
  total_credits: number
  rank: number
  avatar?: string
}

interface UserRank {
  rank: number
  name: string
  credits: number
  team?: string
  avatar?: string
}

const mockTeams: Team[] = [
  { id: 'team-1', name: 'NextEleven Research', description: 'Official NextEleven team', members: 47, total_credits: 2847392, rank: 1 },
  { id: 'team-2', name: 'MIT Cancer Lab', description: 'Koch Institute volunteers', members: 123, total_credits: 1923847, rank: 2 },
  { id: 'team-3', name: 'Stanford Folding', description: 'Folding@home alumni', members: 89, total_credits: 1567234, rank: 3 },
  { id: 'team-4', name: 'Open Science Grid', description: 'Distributed computing enthusiasts', members: 234, total_credits: 1234567, rank: 4 },
  { id: 'team-5', name: 'Reddit r/science', description: 'Community team', members: 567, total_credits: 987654, rank: 5 },
  { id: 'team-6', name: 'Hacker News', description: 'Y Combinator community', members: 445, total_credits: 876543, rank: 6 },
  { id: 'team-7', name: 'University of Tokyo', description: 'RIKEN volunteers', members: 67, total_credits: 765432, rank: 7 },
  { id: 'team-8', name: 'CERN OpenLab', description: 'Particle physics community', members: 89, total_credits: 654321, rank: 8 },
]

const mockUserRanks: UserRank[] = [
  { rank: 1, name: 'compute_maxi', credits: 342156, team: 'NextEleven Research' },
  { rank: 2, name: 'folding_legend', credits: 298734, team: 'Stanford Folding' },
  { rank: 3, name: 'gpu_whisperer', credits: 267891, team: 'MIT Cancer Lab' },
  { rank: 4, name: 'protein_folder', credits: 234567, team: 'Open Science Grid' },
  { rank: 5, name: 'cure_seeker', credits: 212345, team: 'Reddit r/science' },
  { rank: 6, name: 'molecule_hunter', credits: 198765, team: 'Hacker News' },
  { rank: 7, name: 'simulation_master', credits: 187654, team: 'CERN OpenLab' },
  { rank: 8, name: 'drug_discoverer', credits: 176543, team: 'University of Tokyo' },
  { rank: 9, name: 'research_volunteer', credits: 165432, team: 'NextEleven Research' },
  { rank: 10, name: 'science_supporter', credits: 154321, team: 'Open Science Grid' },
]

export default function TeamLeaderboard() {
  const [activeTab, setActiveTab] = useState<'teams' | 'individuals'>('teams')

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold mb-2">Leaderboards</h1>
          <p className="text-text-muted">Compete with teams and individuals worldwide. Validated compute earns credits.</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setActiveTab('teams')}
            className={cn(
              'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
              activeTab === 'teams' ? 'bg-primary text-white' : 'bg-surface-elevated text-text hover:bg-surface'
            )}
          >
            Teams
          </button>
          <button
            onClick={() => setActiveTab('individuals')}
            className={cn(
              'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
              activeTab === 'individuals' ? 'bg-primary text-white' : 'bg-surface-elevated text-text hover:bg-surface'
            )}
          >
            Individuals
          </button>
        </div>
      </div>

      {activeTab === 'teams' && (
        <div className="glass rounded-xl border border-border/50 overflow-hidden">
          <div className="grid grid-cols-[auto_1fr_auto_auto] gap-4 p-4 text-sm font-medium text-text-muted border-b border-border/50">
            <div className="w-10 text-center">#</div>
            <div>Team</div>
            <div className="text-right">Members</div>
            <div className="text-right w-40">Credits</div>
          </div>
          <div className="divide-y divide-border/50">
            {mockTeams.map((team, index) => (
              <div key={team.id} className="grid grid-cols-[auto_1fr_auto_auto] gap-4 p-4 items-center hover:bg-surface/30 transition-colors">
                <div className={cn('w-10 text-center font-bold text-lg', team.rank <= 3 ? 'text-warning' : 'text-text-muted')}>
                  {team.rank === 1 && <Medal className="w-5 h-5 mx-auto text-warning" />}
                  {team.rank === 2 && <Medal className="w-5 h-5 mx-auto text-gray-400" />}
                  {team.rank === 3 && <Medal className="w-5 h-5 mx-auto text-amber-700" />}
                  {team.rank > 3 && team.rank}
                </div>
                <div className="flex items-center gap-3 min-w-0">
                  <div className={cn('w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0', team.rank <= 3 ? 'bg-warning/20 text-warning' : 'bg-primary/20 text-primary')}>
                    {team.name.charAt(0)}
                  </div>
                  <div className="min-w-0">
                    <p className="font-medium truncate">{team.name}</p>
                    <p className="text-xs text-text-muted truncate">{team.description}</p>
                  </div>
                </div>
                <div className="text-right text-sm">
                  <p className="font-mono font-medium">{team.members}</p>
                  <p className="text-xs text-text-muted">members</p>
                </div>
                <div className="text-right w-40">
                  <p className="font-mono font-medium text-primary">{team.total_credits.toLocaleString()}</p>
                  <p className="text-xs text-text-muted">total credits</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'individuals' && (
        <div className="glass rounded-xl border border-border/50 overflow-hidden">
          <div className="grid grid-cols-[auto_1fr_auto_auto] gap-4 p-4 text-sm font-medium text-text-muted border-b border-border/50">
            <div className="w-10 text-center">#</div>
            <div>Volunteer</div>
            <div className="text-right">Team</div>
            <div className="text-right w-40">Credits</div>
          </div>
          <div className="divide-y divide-border/50">
            {mockUserRanks.map((user, index) => (
              <div key={user.rank} className="grid grid-cols-[auto_1fr_auto_auto] gap-4 p-4 items-center hover:bg-surface/30 transition-colors">
                <div className={cn('w-10 text-center font-bold text-lg', user.rank <= 3 ? 'text-warning' : 'text-text-muted')}>
                  {user.rank === 1 && <Trophy className="w-5 h-5 mx-auto text-warning" />}
                  {user.rank === 2 && <Trophy className="w-5 h-5 mx-auto text-gray-400" />}
                  {user.rank === 3 && <Trophy className="w-5 h-5 mx-auto text-amber-700" />}
                  {user.rank > 3 && user.rank}
                </div>
                <div className="flex items-center gap-3 min-w-0">
                  <div className={cn('w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0', user.rank <= 3 ? 'bg-warning/20 text-warning' : 'bg-primary/20 text-primary')}>
                    {user.name.charAt(0)}
                  </div>
                  <div className="min-w-0">
                    <p className="font-medium truncate">{user.name}</p>
                  </div>
                </div>
                <div className="text-right text-sm text-text-muted">
                  <p className="truncate max-w-[120px]">{user.team || 'Independent'}</p>
                </div>
                <div className="text-right w-40">
                  <p className="font-mono font-medium text-primary">{user.credits.toLocaleString()}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Create/Join Team */}
      <div className="glass rounded-xl p-6 border border-border/50">
        <h3 className="font-semibold mb-4">Join or Create a Team</h3>
        <p className="text-text-muted mb-4">
          Teams pool credits for friendly competition. Schools, companies, labs, and communities welcome.
        </p>
        <div className="flex flex-wrap gap-3">
          <button className="px-4 py-2 rounded-lg bg-primary text-white font-medium hover:bg-primary-dark transition-colors">
            Create Team
          </button>
          <button className="px-4 py-2 rounded-lg bg-surface-elevated text-text font-medium hover:bg-surface transition-colors border border-border">
            Browse Teams
          </button>
          <button className="px-4 py-2 rounded-lg bg-surface-elevated text-text font-medium hover:bg-surface transition-colors border border-border">
            Invite Members
          </button>
        </div>
      </div>
    </div>
  )
}