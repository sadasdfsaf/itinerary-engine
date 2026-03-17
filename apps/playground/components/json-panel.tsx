type JsonPanelProps = {
  title: string;
  data: unknown;
};

export function JsonPanel({ title, data }: JsonPanelProps) {
  return (
    <section className="panel">
      <div className="panel-header">
        <p className="eyebrow">{title}</p>
      </div>
      <pre className="json">{JSON.stringify(data, null, 2)}</pre>
    </section>
  );
}
