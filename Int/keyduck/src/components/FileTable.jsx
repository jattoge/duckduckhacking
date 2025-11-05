// src/components/FileTable.jsx
import React, { useEffect, useState } from "react";

export default function FileTable() {
  const [files, setFiles] = useState([]);

  // Decodifica cada linha Base64 individualmente
  const decodeBase64Lines = (content) => {
    try {
      return content
        .split(/\r?\n/) // divide por linha
        .filter((line) => line.trim() !== "") // ignora linhas vazias
        .map((line) => {
          try {
            return atob(line.trim()); // decodifica cada linha
          } catch {
            return `[Erro ao decodificar linha: ${line}]`;
          }
        })
        .join("\n"); // junta tudo novamente
    } catch (err) {
      console.error("Erro ao processar Base64:", err);
      return "[Erro ao decodificar arquivo]";
    }
  };

  useEffect(() => {
    // importa todos os arquivos .txt da pasta Comunicacao (raw)
    const modules = import.meta.glob("../assets/Comunicacao/*.txt", { as: "raw" });

    Promise.all(
      Object.entries(modules).map(async ([path, loader]) => {
        const name = path.split("/").pop();

        // Pula explicitamente Shhh.txt
        if (name === "Shhh.txt") {
          return null; // retornamos null para filtrar depois
        }

        const encodedContent = await loader(); // conteúdo original (Base64 por linha)
        const decodedContent = decodeBase64Lines(encodedContent); // decodifica por linha

        return {
          name,
          size: encodedContent.length,
          lastModifiedDate: new Date(),
          content: decodedContent,
        };
      })
    )
      .then((maybeFiles) => {
        // filtra os nulls (arquivos pulados) e seta o estado
        const loadedFiles = maybeFiles.filter(Boolean);
        setFiles(loadedFiles);
      })
      .catch((err) => {
        console.error("Erro ao carregar arquivos:", err);
      });
  }, []);

  return (
    <div
      style={{
        padding: 16,
        fontFamily: "Arial, sans-serif",
        backgroundColor: "#32323e",
        minHeight: "100vh",
      }}
    >
      <h2 style={{ marginBottom: 12, color: "#fff" }}>Histórico</h2>

      {files.length === 0 ? (
        <p style={{ color: "#ccc" }}>Nenhum arquivo encontrado.</p>
      ) : (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: 16,
            width: "100%",
            maxWidth: 800,
            margin: "0 auto",
          }}
        >
          {files.map((f, idx) => (
            <div
              key={idx}
              style={{
                border: "1px solid #ccc",
                borderRadius: 12,
                padding: 16,
                background: "#f9f9f9",
                boxShadow: "0 2px 6px rgba(0,0,0,0.1)",
                transition: "transform 0.2s, box-shadow 0.2s",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = "translateY(-3px)";
                e.currentTarget.style.boxShadow =
                  "0 4px 10px rgba(0,0,0,0.15)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = "translateY(0)";
                e.currentTarget.style.boxShadow =
                  "0 2px 6px rgba(0,0,0,0.1)";
              }}
            >
              <h3 style={{ margin: "0 0 8px 0", color: "#333" }}>{f.name}</h3>

              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: 2,
                  fontSize: 14,
                  color: "#555",
                }}
              >
                <span>
                  <strong>Tamanho:</strong> {f.size} bytes
                </span>
                <span>
                  <strong>Modificado:</strong>{" "}
                  {f.lastModifiedDate.toLocaleString()}
                </span>
              </div>

              <details style={{ marginTop: 10 }}>
                <summary
                  style={{
                    cursor: "pointer",
                    color: "#007bff",
                    fontSize: 14,
                    fontWeight: "bold",
                  }}
                >
                  Ver conteúdo
                </summary>
                <pre
                  style={{
                    whiteSpace: "pre-wrap",
                    background: "#d1d1d1f1",
                    borderColor: "#007bff",
                    borderRadius: 6,
                    padding: 10,
                    marginTop: 8,
                    maxHeight: 800,
                    overflow: "auto",
                    fontSize: 13,
                  }}
                >
                  {f.content}
                </pre>
              </details>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
