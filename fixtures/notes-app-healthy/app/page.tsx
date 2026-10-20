import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import { createNote, deleteNote } from "./notes/actions";

export default async function Home() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) redirect("/login");

  const { data: notes } = await supabase
    .from("notes")
    .select("id, title, body, created_at")
    .order("created_at", { ascending: false });

  return (
    <main>
      <h1>My notes</h1>
      <form action={createNote}>
        <input name="title" placeholder="Title" required />
        <textarea name="body" placeholder="Write something" />
        <button type="submit">Add note</button>
      </form>
      <ul>
        {(notes ?? []).map((n) => (
          <li key={n.id}>
            <strong>{n.title}</strong>
            <p>{n.body}</p>
            <form action={deleteNote.bind(null, n.id)}>
              <button type="submit">Delete</button>
            </form>
          </li>
        ))}
      </ul>
    </main>
  );
}
