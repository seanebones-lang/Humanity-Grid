import { ProjectStory, ContributionStats } from '@/types'
import { FlaskConical, Clock, Target, Award, ArrowRight, BarChart3 } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ProjectStoriesProps {
  stories: ProjectStory[]
  contributions: ContributionStats | null
}

export default function ProjectStories({ stories, contributions }: ProjectStoriesProps) {
  const displayStories = stories

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold mb-2">Your Impact</h1>
        <p className="text-text-muted">Real research your computer has contributed to. Every molecule screened brings us closer to treatments.</p>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass rounded-xl p-5 border border-border/50">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-text-muted">Molecules Screened</p>
              <p className="font-mono text-2xl font-bold">{displayStories.reduce((sum, s) => sum + s.molecules_screened, 0).toLocaleString()}</p>
            </div>
            <div className="p-2 rounded-lg bg-primary/10"><Target className="w-5 h-5 text-primary" /></div>
          </div>
        </div>
        <div className="glass rounded-xl p-5 border border-border/50">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-text-muted">Hours Donated</p>
              <p className="font-mono text-2xl font-bold">{displayStories.reduce((sum, s) => sum + s.hours_donated, 0).toFixed(1)}</p>
            </div>
            <div className="p-2 rounded-lg bg-success/10"><Clock className="w-5 h-5 text-success" /></div>
          </div>
        </div>
        <div className="glass rounded-xl p-5 border border-border/50">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-text-muted">Projects Supported</p>
              <p className="font-mono text-2xl font-bold">{displayStories.length}</p>
            </div>
            <div className="p-2 rounded-lg bg-warning/10"><FlaskConical className="w-5 h-5 text-warning" /></div>
          </div>
        </div>
        <div className="glass rounded-xl p-5 border border-border/50">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-text-muted">Studies Published</p>
              <p className="font-mono text-2xl font-bold">{contributions?.papers_published ?? displayStories.filter(s => s.status.includes('published')).length}</p>
            </div>
            <div className="p-2 rounded-lg bg-primary-light/10"><Award className="w-5 h-5 text-primary-light" /></div>
          </div>
        </div>
      </div>

      {/* Project Cards */}
      <div className="space-y-4">
        {displayStories.map((story) => (
          <div key={story.project_id} className="glass rounded-xl p-6 border border-border/50 hover:border-primary/30 transition-colors">
            <div className="flex flex-col lg:flex-row lg:items-start gap-6">
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h3 className="font-semibold text-lg mb-1">{story.title}</h3>
                    <p className="text-sm text-text-muted">Project {story.project_id}</p>
                  </div>
                  <span className={cn(
                    'px-3 py-1 rounded-full text-xs font-medium whitespace-nowrap',
                    story.status.includes('published') || story.status.includes('validated') ? 'bg-success/20 text-success' :
                    story.status.includes('progress') || story.status.includes('underway') || story.status.includes('planned') ? 'bg-warning/20 text-warning' :
                    'bg-primary/20 text-primary'
                  )}>
                    {story.status}
                  </span>
                </div>
                <p className="text-text-muted mt-2 mb-4">{story.description}</p>
                <div className="glass rounded-lg p-4 border border-border/50">
                  <p className="text-sm text-text-muted mb-2">Your personal contribution:</p>
                  <p className="text-text">{story.your_contribution}</p>
                </div>
              </div>
              <div className="flex lg:flex-col items-end lg:items-center gap-4 shrink-0">
                <div className="grid grid-cols-3 gap-4 text-center w-full lg:w-auto">
                  <div className="p-3 rounded-lg bg-surface/50">
                    <p className="font-mono text-xl font-bold">{story.molecules_screened.toLocaleString()}</p>
                    <p className="text-xs text-text-muted">Molecules</p>
                  </div>
                  <div className="p-3 rounded-lg bg-surface/50">
                    <p className="font-mono text-xl font-bold">{story.hours_donated.toFixed(1)}h</p>
                    <p className="text-xs text-text-muted">Hours</p>
                  </div>
                  <div className="p-3 rounded-lg bg-surface/50">
                    <p className="font-mono text-xl font-bold">{story.project_id}</p>
                    <p className="text-xs text-text-muted">Project</p>
                  </div>
                </div>
                <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary/10 text-primary hover:bg-primary/20 text-sm font-medium transition-colors w-full lg:w-auto">
                  <span>View Details</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* CTA */}
      <div className="glass rounded-xl p-6 border border-border/50 text-center">
        <div className="p-2 rounded-lg bg-primary/10 inline-flex mb-4"><BarChart3 className="w-6 h-6 text-primary" /></div>
        <h3 className="font-semibold text-lg mb-2">Want to see more?</h3>
        <p className="text-text-muted mb-4 max-w-md mx-auto">
          Visit the Humanity Grid web portal to explore all projects, download raw data, and read published papers.
        </p>
        <a href="https://humanity-grid.org/projects" target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-white font-medium hover:bg-primary-dark transition-colors">
          Explore All Projects
          <ArrowRight className="w-4 h-4" />
        </a>
      </div>
    </div>
  )
}