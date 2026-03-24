"""
services/folder_service.py
All business logic for folder CRUD and tree traversal.
Uses psycopg2 (%s placeholders).
"""
from typing import Optional, List, Tuple

from database.connection import get_conn
from models.folder import Folder


class FolderService:

    def get_roots(self) -> List[Folder]:
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM folders WHERE parent_id IS NULL ORDER BY name")
            return [Folder.from_row(r) for r in cur.fetchall()]
        finally:
            conn.close()

    def get_children(self, parent_id: int) -> List[Folder]:
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM folders WHERE parent_id = %s ORDER BY name",
                (parent_id,)
            )
            return [Folder.from_row(r) for r in cur.fetchall()]
        finally:
            conn.close()

    def get_by_id(self, folder_id: int) -> Optional[Folder]:
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM folders WHERE id = %s", (folder_id,))
            row = cur.fetchone()
            return Folder.from_row(row) if row else None
        finally:
            conn.close()

    def create(
        self,
        name: str,
        created_by: str,
        parent_id: Optional[int] = None,
        description: Optional[str] = None,
    ) -> Tuple[bool, str]:
        if not name.strip():
            return False, "Folder name cannot be empty."
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO folders (name, parent_id, description, created_by) VALUES (%s, %s, %s, %s)",
                (name.strip(), parent_id, description, created_by),
            )
            conn.commit()
            return True, "Folder created."
        except Exception:
            conn.rollback()
            return False, "A folder with that name already exists here."
        finally:
            conn.close()

    def update(self, folder_id: int, name: str, description: Optional[str]) -> Tuple[bool, str]:
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE folders SET name = %s, description = %s WHERE id = %s",
                (name.strip(), description, folder_id),
            )
            conn.commit()
            return True, "Folder updated."
        except Exception:
            conn.rollback()
            return False, "A folder with that name already exists."
        finally:
            conn.close()

    def delete(self, folder_id: int) -> Tuple[bool, str]:
        """Cascades to children, queries, and versions via FK ON DELETE CASCADE."""
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM folders WHERE id = %s", (folder_id,))
            conn.commit()
            return True, "Folder deleted."
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()

    def get_path(self, folder_id: int) -> str:
        """Return breadcrumb string: RootFolder / Child / Grandchild"""
        parts = []
        fid = folder_id
        conn = get_conn()
        try:
            cur = conn.cursor()
            while fid:
                cur.execute("SELECT * FROM folders WHERE id = %s", (fid,))
                row = cur.fetchone()
                if not row:
                    break
                parts.insert(0, row["name"])
                fid = row["parent_id"]
        finally:
            conn.close()
        return " / ".join(parts)

    def get_tree_nested(self) -> List[Folder]:
        """
        Fetch all folders and return a nested tree structure (list of roots).
        Each folder object will have a 'children' list attribute attached.
        """
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM folders ORDER BY name")
            all_folders = [Folder.from_row(r) for r in cur.fetchall()]
        finally:
            conn.close()

        id_map = {f.id: f for f in all_folders}
        roots = []

        for f in all_folders:
            f.children = []

        for f in all_folders:
            if f.parent_id and f.parent_id in id_map:
                id_map[f.parent_id].children.append(f)
            else:
                roots.append(f)

        return roots

    def walk_tree(self, parent_id: Optional[int] = None, depth: int = 0):
        """
        Generator that yields (Folder, depth) in DFS order.
        """
        folders = self.get_roots() if parent_id is None else self.get_children(parent_id)
        for folder in folders:
            yield folder, depth
            yield from self.walk_tree(folder.id, depth + 1)


folder_service = FolderService()
