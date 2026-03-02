import { NavLink } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  LayoutDashboard,
  Brain,
  Target,
  Award,
  Wrench,
  AlertTriangle,
  Shield,
  Activity,
  Download,
  Upload,
  FileSpreadsheet,
  CheckCircle2,
  Factory,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useEffect, useState, useRef } from 'react'
import { systemApi } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Dialog } from '@/components/ui/dialog'
import { useSystemStore } from '@/store/systemStore'

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Control Room' },
  { to: '/prediction', icon: Brain, label: 'Prediction' },
  { to: '/optimization', icon: Target, label: 'Optimization' },
  { to: '/golden-signature', icon: Award, label: 'Golden Signature' },
  { to: '/correction', icon: Wrench, label: 'Real-Time Correction' },
  { to: '/anomaly', icon: AlertTriangle, label: 'Anomaly & Reliability' },
  { to: '/governance', icon: Shield, label: 'Model Governance' },
  { to: '/industrial-validation', icon: Factory, label: 'Industrial Validation' },
]

export function Sidebar() {
  const [dataFiles, setDataFiles] = useState<Array<{ name: string; size: number; modified: number }>>([])
  const [uploading, setUploading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [selectedFiles, setSelectedFiles] = useState<{ production?: File; process?: File }>({})
  const [successDialog, setSuccessDialog] = useState<{
    isOpen: boolean
    batchCount: number
    classifications: Array<{ filename: string; type: string }>
  }>({
    isOpen: false,
    batchCount: 0,
    classifications: [],
  })
  const [errorDialog, setErrorDialog] = useState<{ isOpen: boolean; message: string }>({
    isOpen: false,
    message: '',
  })
  const { setProcessing } = useSystemStore()

  useEffect(() => {
    loadDataFiles()
  }, [])

  const loadDataFiles = async () => {
    try {
      const response = await systemApi.getDataFiles()
      setDataFiles(response.files)
    } catch (error) {
      console.error('Failed to load data files:', error)
    }
  }

  const handleDownload = async (filename: string) => {
    try {
      await systemApi.downloadDataFile(filename)
    } catch (error) {
      alert('Failed to download file')
    }
  }

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (!files || files.length !== 2) {
      alert('Please select exactly 2 Excel files')
      return
    }

    const fileArray = Array.from(files)
    
    // Accept any 2 xlsx files - backend will classify them
    setSelectedFiles({ 
      production: fileArray[0], 
      process: fileArray[1] 
    })
  }

  const handleUpload = async () => {
    if (!selectedFiles.production || !selectedFiles.process) {
      setErrorDialog({
        isOpen: true,
        message: 'Please select both files',
      })
      return
    }

    setUploading(true)
    setProcessing(true, 'Uploading files and retraining models...')
    try {
      const result = await systemApi.uploadDataFiles(selectedFiles.production, selectedFiles.process)
      
      // Build classification info
      const classifications = Object.entries(result.classified_as).map(([filename, type]) => ({
        filename,
        type: type as string,
      }))
      
      setSuccessDialog({
        isOpen: true,
        batchCount: result.batches_loaded,
        classifications,
      })
      
      setSelectedFiles({})
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
      loadDataFiles()
    } catch (error: any) {
      console.error('Upload error:', error)
      let errorMsg = 'Upload failed: '
      
      if (error.message) {
        errorMsg += error.message
      } else {
        errorMsg += 'Unknown error occurred'
      }
      
      setErrorDialog({
        isOpen: true,
        message: errorMsg,
      })
    } finally {
      setUploading(false)
      setProcessing(false)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  const formatDate = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleDateString()
  }

  return (
    <>
    <motion.aside
      initial={{ x: -300 }}
      animate={{ x: 0 }}
      className="w-64 border-r border-border bg-card/50 backdrop-blur-xl flex flex-col"
    >
      <div className="flex h-16 items-center gap-2 border-b border-border px-6">
        <Activity className="h-8 w-8 text-teal-500 animate-pulse-glow" />
        <div>
          <h1 className="text-lg font-bold">Manufacturing AI</h1>
          <p className="text-xs text-muted-foreground">Intelligence System</p>
        </div>
      </div>

      <nav className="space-y-1 p-4 flex-1">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-all',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
              )
            }
          >
            {({ isActive }) => (
              <>
                <item.icon className="h-5 w-5" />
                <span>{item.label}</span>
                {isActive && (
                  <motion.div
                    layoutId="activeNav"
                    className="ml-auto h-2 w-2 rounded-full bg-neon-green"
                  />
                )}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-border bg-card/80 p-3">
        <div className="text-xs">
          <div className="font-semibold mb-2 text-muted-foreground">Data Sources</div>
          
          {dataFiles.length === 0 ? (
            <div className="mb-3 p-2 rounded bg-red-500/10 border border-red-500/20">
              <div className="text-[10px] text-red-400 font-medium">
                ⚠ No data sources found
              </div>
              <div className="text-[9px] text-red-400/70 mt-1">
                Please upload Excel files to begin
              </div>
            </div>
          ) : (
            <div className="space-y-1.5">
              {dataFiles.map((file) => (
                <div
                  key={file.name}
                  className="flex items-start gap-2 p-2 rounded bg-background/50 hover:bg-background/80 transition-colors cursor-pointer group"
                  onClick={() => handleDownload(file.name)}
                >
                  <FileSpreadsheet className="h-4 w-4 text-teal-500 flex-shrink-0 mt-0.5" />
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-[10px] truncate group-hover:text-teal-500 transition-colors">
                      {file.name}
                    </div>
                    <div className="text-[9px] text-muted-foreground">
                      {formatFileSize(file.size)} • {formatDate(file.modified)}
                    </div>
                  </div>
                  <Download className="h-3 w-3 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0 mt-0.5" />
                </div>
              ))}
            </div>
          )}

          <div className="mt-3 space-y-2">
            <input
              ref={fileInputRef}
              type="file"
              accept=".xlsx"
              multiple
              onChange={handleFileSelect}
              className="hidden"
              id="file-upload"
            />
            <label
              htmlFor="file-upload"
              className="flex items-center justify-center gap-2 px-3 py-2 rounded bg-accent hover:bg-accent/80 transition-colors cursor-pointer text-[11px] font-medium"
            >
              <Upload className="h-3.5 w-3.5" />
              Select 2 Excel Files
            </label>
            <div className="text-[9px] text-muted-foreground text-center opacity-70">
              Auto-classifies production & process data
            </div>

            {(selectedFiles.production || selectedFiles.process) && (
              <div className="space-y-1">
                <div className="text-[9px] text-muted-foreground font-semibold">
                  Files ready:
                </div>
                {selectedFiles.production && (
                  <div className="text-[9px] text-muted-foreground truncate">
                    ✓ {selectedFiles.production.name}
                  </div>
                )}
                {selectedFiles.process && (
                  <div className="text-[9px] text-muted-foreground truncate">
                    ✓ {selectedFiles.process.name}
                  </div>
                )}
                <Button
                  onClick={handleUpload}
                  disabled={uploading}
                  size="sm"
                  className="w-full h-8 text-[11px]"
                >
                  {uploading ? 'Uploading & Retraining...' : 'Upload & Reload System'}
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </motion.aside>

    {/* Success Dialog */}
    <Dialog
      isOpen={successDialog.isOpen}
      onClose={() => setSuccessDialog({ isOpen: false, batchCount: 0, classifications: [] })}
      title="Upload Successful!"
    >
      <div className="space-y-4">
        <div className="flex items-center gap-3 p-4 rounded-lg bg-neon-green/10 border border-neon-green/30">
          <CheckCircle2 className="h-8 w-8 text-neon-green flex-shrink-0" />
          <div>
            <p className="font-semibold text-neon-green">System Reloaded Successfully</p>
            <p className="text-sm text-muted-foreground mt-1">
              {successDialog.batchCount} batches loaded
            </p>
          </div>
        </div>

        <div className="space-y-2">
          <p className="text-sm font-medium">Auto-classification Results:</p>
          <div className="space-y-2">
            {successDialog.classifications.map((item, idx) => (
              <div
                key={idx}
                className="flex items-center gap-2 p-3 rounded bg-background/50 border border-border/50"
              >
                <FileSpreadsheet className="h-4 w-4 text-teal-500 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-medium truncate">{item.filename}</p>
                  <p className="text-xs text-muted-foreground">
                    → {item.type} data
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="p-3 rounded bg-primary/10 border border-primary/20">
          <p className="text-xs text-muted-foreground">
            ✓ Data pipeline rebuilt<br />
            ✓ Models retrained<br />
            ✓ System ready for operation
          </p>
        </div>

        <Button
          onClick={() => setSuccessDialog({ isOpen: false, batchCount: 0, classifications: [] })}
          className="w-full"
          variant="neon"
        >
          Continue
        </Button>
      </div>
    </Dialog>

    {/* Error Dialog */}
    <Dialog
      isOpen={errorDialog.isOpen}
      onClose={() => setErrorDialog({ isOpen: false, message: '' })}
      title="Upload Failed"
      variant="destructive"
    >
      <div className="space-y-4">
        <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30">
          <p className="text-sm text-red-400">{errorDialog.message}</p>
        </div>
        <Button
          onClick={() => setErrorDialog({ isOpen: false, message: '' })}
          className="w-full"
          variant="outline"
        >
          Close
        </Button>
      </div>
    </Dialog>
  </>
  )
}
