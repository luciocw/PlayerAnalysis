"use client"

import { useState, useRef, useCallback } from "react"
import { UploadCloud, FileVideo, AlertCircle, X } from "lucide-react"
import { useChunkedUpload } from "@/hooks/useChunkedUpload"

const TWO_GB = 2 * 1024 * 1024 * 1024

type Props = {
  onUploadComplete: (sessionId: string) => void
  fieldWidthM: number
  fieldHeightM: number
}

function formatFileSize(bytes: number): string {
  if (bytes >= 1024 * 1024 * 1024) {
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`
  }
  if (bytes >= 1024 * 1024) {
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }
  return `${(bytes / 1024).toFixed(0)} KB`
}

export function UploadZone({ onUploadComplete, fieldWidthM, fieldHeightM }: Props) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isDragOver, setIsDragOver] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { upload, progress, isUploading, error } = useChunkedUpload()

  const handleFileSelect = useCallback((file: File) => {
    if (!file.type.startsWith("video/")) return
    setSelectedFile(file)
  }, [])

  function handleDragOver(e: React.DragEvent) {
    e.preventDefault()
    setIsDragOver(true)
  }

  function handleDragLeave(e: React.DragEvent) {
    e.preventDefault()
    setIsDragOver(false)
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault()
    setIsDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFileSelect(file)
  }

  function handleInputChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (file) handleFileSelect(file)
  }

  function handleZoneClick() {
    fileInputRef.current?.click()
  }

  function handleRemoveFile() {
    setSelectedFile(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  async function handleUpload() {
    if (!selectedFile) return

    try {
      const sessionId = await upload(selectedFile, fieldWidthM, fieldHeightM)
      onUploadComplete(sessionId)
    } catch {
      // error is set inside the hook
    }
  }

  if (isUploading) {
    return (
      <div className="bg-gray-900 rounded-xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-8 h-8 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin shrink-0" />
          <div>
            <p className="text-sm font-medium text-white">
              Enviando {selectedFile?.name}
            </p>
            <p className="text-xs text-gray-400">
              {Math.round(progress)}% concluído
            </p>
          </div>
        </div>

        <div className="w-full bg-gray-800 rounded-full h-2.5">
          <div
            className="bg-emerald-500 h-2.5 rounded-full transition-all duration-300"
            style={{ width: `${Math.max(2, progress)}%` }}
          />
        </div>

        <p className="text-xs text-gray-500 mt-3">
          Não feche esta página durante o upload.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {!selectedFile ? (
        <div
          role="button"
          tabIndex={0}
          onClick={handleZoneClick}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") handleZoneClick()
          }}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`relative border-2 border-dashed rounded-xl p-10 flex flex-col items-center justify-center cursor-pointer transition-colors ${
            isDragOver
              ? "border-emerald-500 bg-emerald-900/10"
              : "border-gray-700 hover:border-gray-500 bg-gray-900/50"
          }`}
        >
          <UploadCloud
            className={`w-10 h-10 mb-3 ${isDragOver ? "text-emerald-400" : "text-gray-500"}`}
          />
          <p className="text-sm font-medium text-gray-300 mb-1">
            Arraste o vídeo aqui ou clique para selecionar
          </p>
          <p className="text-xs text-gray-500">Apenas arquivos de vídeo</p>

          <input
            ref={fileInputRef}
            type="file"
            accept="video/*"
            className="hidden"
            onChange={handleInputChange}
          />
        </div>
      ) : (
        <div className="bg-gray-900 rounded-xl p-4 flex items-center gap-3">
          <div className="w-10 h-10 bg-gray-800 rounded-lg flex items-center justify-center shrink-0">
            <FileVideo className="w-5 h-5 text-emerald-400" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-white truncate">
              {selectedFile.name}
            </p>
            <p className="text-xs text-gray-400">
              {formatFileSize(selectedFile.size)}
            </p>
          </div>
          <button
            onClick={handleRemoveFile}
            className="text-gray-500 hover:text-gray-300 transition-colors p-1"
            aria-label="Remover arquivo"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {selectedFile && selectedFile.size > TWO_GB && (
        <div className="flex items-start gap-2 bg-yellow-950/40 border border-yellow-800 rounded-lg p-3 text-xs">
          <AlertCircle className="w-4 h-4 text-yellow-400 mt-0.5 shrink-0" />
          <p className="text-yellow-300">
            Arquivos grandes podem demorar para fazer upload.
          </p>
        </div>
      )}

      {error && (
        <div className="flex items-start gap-2 bg-red-950/40 border border-red-800 rounded-lg p-3 text-xs">
          <AlertCircle className="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
          <p className="text-red-300">{error}</p>
        </div>
      )}

      {selectedFile && (
        <button
          onClick={() => void handleUpload()}
          disabled={isUploading}
          className="w-full bg-emerald-600 hover:bg-emerald-500 disabled:bg-gray-700 disabled:text-gray-500 disabled:cursor-not-allowed text-white font-medium py-3 rounded-xl transition-colors text-sm"
        >
          Iniciar Upload
        </button>
      )}
    </div>
  )
}
