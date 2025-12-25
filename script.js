// Daftar file .txt (kamu bisa hardcode atau fetch dinamis jika banyak)
const posts = [
    { title: "Postingan Pertama", file: "posts/post1.txt", slug: "post1" },
    { title: "Postingan Kedua", file: "posts/post2.txt", slug: "post2" }
    // Tambah manual di sini saat buat post baru
];

const postList = document.getElementById('post-list');

posts.forEach(post => {
    const li = document.createElement('li');
    const a = document.createElement('a');
    a.href = `post.html?slug=${post.slug}`;  // Link ke halaman post
    a.textContent = post.title;
    li.appendChild(a);
    postList.appendChild(li);
});
