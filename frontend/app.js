
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer();

renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Nodes
const nodes = [];
const geometry = new THREE.SphereGeometry(0.5);
const material = new THREE.MeshBasicMaterial();

for (let i = 0; i < 10; i++) {
    const node = new THREE.Mesh(geometry, material.clone());
    node.position.x = (Math.random() - 0.5) * 10;
    node.position.y = (Math.random() - 0.5) * 10;
    scene.add(node);
    nodes.push(node);
}

// Lines (connections)
const lines = [];
nodes.forEach((n1, i) => {
    nodes.forEach((n2, j) => {
        if (i < j && Math.random() > 0.7) {
            const material = new THREE.LineBasicMaterial();
            const points = [];
            points.push(n1.position);
            points.push(n2.position);
            const geometry = new THREE.BufferGeometry().setFromPoints(points);
            const line = new THREE.Line(geometry, material);
            scene.add(line);
            lines.push(line);
        }
    });
});

// Animation (propagation pulse)
function animate() {
    requestAnimationFrame(animate);

    nodes.forEach(node => {
        node.scale.x = 1 + Math.sin(Date.now() * 0.002) * 0.3;
        node.scale.y = node.scale.x;
        node.scale.z = node.scale.x;
    });

    renderer.render(scene, camera);
}

camera.position.z = 15;

animate();
