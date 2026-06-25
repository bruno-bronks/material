export type PaperItem = {
  source?: string;
  title?: string;
  authors?: string[];
  year?: string | number;
  doi?: string;
  url?: string;
};

export default function PaperCard({ paper }: { paper: PaperItem }) {
  const link = paper.url || (paper.doi ? `https://doi.org/${paper.doi}` : null);
  const authors = paper.authors ?? [];
  const authorLabel = authors.length > 0 ? (authors.length > 1 ? `${authors[0]} et al.` : authors[0]) : null;
  const meta = [paper.source, paper.year, authorLabel].filter(Boolean).join(" · ");

  return (
    <div className="paper-card">
      {link ? (
        <a href={link} target="_blank" rel="noopener noreferrer" className="paper-card-title">
          {paper.title}
        </a>
      ) : (
        <span className="paper-card-title">{paper.title}</span>
      )}
      {meta && <div className="paper-card-meta">{meta}</div>}
    </div>
  );
}
