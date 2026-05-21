/**
 * LE DERNIER SURVIVANT - Moteur de Jeu
 * Réalisé en HTML5 Canvas & JavaScript pur.
 * Style minimaliste : lignes de néon blanches sur fond noir, atmosphère tendue.
 */

// Fonction d'initialisation du jeu complet
function initGame() {
    console.log("Initialisation du jeu en cours...");

    // --- CONFIGURATION & CONSTANTES ---
    const TILE_SIZE = 80;
    const MAP_COLS = 25;
    const MAP_ROWS = 20;
    const MAP_WIDTH = MAP_COLS * TILE_SIZE;
    const MAP_HEIGHT = MAP_ROWS * TILE_SIZE;

    // --- PLAN DE LA CARTE ---
    const MAP_LAYOUT = [
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1],
        [1,0,E,0,1,0,1,1,1,0,1,1,1,0,1,0,1,1,1,0,1,0,X,0,1],
        [1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1],
        [1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,1,1,0,1,0,1,1,1,1,1],
        [1,0,0,0,0,0,1,0,1,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,1],
        [1,0,1,1,1,0,1,0,1,0,M,0,1,0,1,1,1,1,1,1,1,1,0,1,1],
        [1,0,1,0,0,0,1,0,1,1,1,1,1,0,1,0,0,0,0,0,0,1,0,1,1],
        [1,0,1,0,1,1,1,0,0,0,0,0,0,0,1,0,M,0,M,0,0,1,0,0,1],
        [1,0,1,0,1,0,0,0,1,1,0,1,1,0,1,1,1,1,1,1,0,1,1,0,1],
        [1,0,0,0,1,0,M,0,1,0,0,0,1,0,0,0,0,0,0,1,0,0,1,0,1],
        [1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,0,0,1,1,0,1,0,1],
        [1,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,1,0,0,1,0,0,1,0,1],
        [1,0,1,1,1,1,1,0,1,1,0,1,1,0,W,0,1,0,1,1,0,1,1,0,1],
        [1,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,1],
        [1,0,1,0,M,0,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,0,1,0,1],
        [1,0,1,1,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,1],
        [1,0,0,0,0,0,1,0,1,1,1,1,1,1,1,1,1,1,0,0,1,0,0,0,1],
        [1,0,0,0,0,0,0,0,1,0,0,0,M,0,0,0,0,1,0,0,0,0,0,0,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    ];

    // --- INITIALISATION DU CANVAS ---
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");
    const container = document.getElementById("canvas-container");

    function resizeCanvas() {
        if (canvas && container) {
            canvas.width = container.clientWidth;
            canvas.height = container.clientHeight;
        }
    }
    window.addEventListener("resize", resizeCanvas);
    resizeCanvas();

    // --- VARIABLES DU MOTEUR DE JEU ---
    let gameState = "MENU"; // MENU, PLAYING, GAMEOVER, VICTORY
    let lastTime = 0;
    let screenShakeTimer = 0;
    let screenShakeIntensity = 0;
    let spawnPoint = { x: 120, y: 120 };
    let exitPortal = null;
    let swordItem = null;
    let player = null;
    let enemies = [];
    let particles = [];
    let walls = [];

    // Éléments du DOM pour l'UI
    const screens = {
        MENU: document.getElementById("mainMenu"),
        GAMEOVER: document.getElementById("gameOver"),
        VICTORY: document.getElementById("victoryMenu")
    };
    const hud = document.getElementById("hud");
    const instructions = document.getElementById("instructions");
    const hpBar = document.getElementById("hpBar");
    const startBtn = document.getElementById("startBtn");
    const restartBtn = document.getElementById("restartBtn");
    const nextLevelBtn = document.getElementById("nextLevelBtn");
    const fullscreenBtn = document.getElementById("fullscreenBtn");

    // --- GESTIONNAIRE D'ENTRÉES (INPUTS) ---
    const keys = {};
    const mouse = { x: 0, y: 0, worldX: 0, worldY: 0, clickLeft: false, clickRight: false };

    window.addEventListener("keydown", (e) => {
        keys[e.key.toLowerCase()] = true;
        if (["arrowup", "arrowdown", "arrowleft", "arrowright", " "].includes(e.key)) {
            e.preventDefault();
        }
    });
    window.addEventListener("keyup", (e) => {
        keys[e.key.toLowerCase()] = false;
    });

    canvas.addEventListener("mousemove", (e) => {
        const rect = canvas.getBoundingClientRect();
        mouse.x = e.clientX - rect.left;
        mouse.y = e.clientY - rect.top;
    });

    canvas.addEventListener("mousedown", (e) => {
        if (gameState !== "PLAYING") return;
        if (e.button === 0) mouse.clickLeft = true;
        if (e.button === 2) mouse.clickRight = true;
    });

    canvas.addEventListener("mouseup", (e) => {
        if (e.button === 0) mouse.clickLeft = false;
        if (e.button === 2) mouse.clickRight = false;
    });

    canvas.addEventListener("contextmenu", (e) => e.preventDefault());

    // Gestion du Plein Écran
    if (fullscreenBtn) {
        fullscreenBtn.addEventListener("click", () => {
            if (!document.fullscreenElement) {
                container.requestFullscreen().catch(err => {
                    console.error(`Erreur d'activation plein écran: ${err.message}`);
                });
            } else {
                document.exitFullscreen();
            }
        });
    }

    // --- CAMÉRA ---
    class Camera {
        constructor() {
            this.x = 0;
            this.y = 0;
        }

        update(targetX, targetY) {
            let idealX = targetX - canvas.width / 2;
            let idealY = targetY - canvas.height / 2;

            if (canvas.width >= MAP_WIDTH) {
                this.x = (MAP_WIDTH - canvas.width) / 2;
            } else {
                this.x = Math.max(0, Math.min(idealX, MAP_WIDTH - canvas.width));
            }

            if (canvas.height >= MAP_HEIGHT) {
                this.y = (MAP_HEIGHT - canvas.height) / 2;
            } else {
                this.y = Math.max(0, Math.min(idealY, MAP_HEIGHT - canvas.height));
            }
        }

        toScreen(worldX, worldY) {
            return {
                x: worldX - this.x,
                y: worldY - this.y
            };
        }

        toWorld(screenX, screenY) {
            return {
                x: screenX + this.x,
                y: screenY + this.y
            };
        }
    }
    const camera = new Camera();

    // --- PARTICULES ---
    class Particle {
        constructor(x, y, vx, vy, color, size, life, decay, isLine = false) {
            this.x = x;
            this.y = y;
            this.vx = vx;
            this.vy = vy;
            this.color = color;
            this.size = size;
            this.maxLife = life;
            this.life = life;
            this.decay = decay;
            this.isLine = isLine;
            this.angle = Math.random() * Math.PI * 2;
            this.spin = (Math.random() - 0.5) * 0.1;
        }

        update(dt) {
            this.x += this.vx * dt * 60;
            this.y += this.vy * dt * 60;
            this.angle += this.spin;
            this.vx *= 0.95;
            this.vy *= 0.95;
            this.life -= this.decay * dt * 60;
        }

        draw(ctx, cam) {
            const screenPos = cam.toScreen(this.x, this.y);
            const alpha = Math.max(0, this.life / this.maxLife);
            
            ctx.save();
            ctx.globalAlpha = alpha;
            ctx.strokeStyle = this.color;
            ctx.fillStyle = this.color;
            ctx.shadowBlur = 8;
            ctx.shadowColor = this.color;
            
            if (this.isLine) {
                ctx.lineWidth = this.size;
                ctx.beginPath();
                ctx.moveTo(screenPos.x, screenPos.y);
                ctx.lineTo(screenPos.x - this.vx * 0.2, screenPos.y - this.vy * 0.2);
                ctx.stroke();
            } else {
                ctx.beginPath();
                ctx.arc(screenPos.x, screenPos.y, this.size, 0, Math.PI * 2);
                ctx.fill();
            }
            ctx.restore();
        }
    }

    function spawnImpactParticles(x, y, count, color = "#ffffff") {
        for (let i = 0; i < count; i++) {
            const angle = Math.random() * Math.PI * 2;
            const speed = 2 + Math.random() * 6;
            const vx = Math.cos(angle) * speed;
            const vy = Math.sin(angle) * speed;
            const size = 1 + Math.random() * 3;
            const life = 1.0;
            const decay = 0.02 + Math.random() * 0.03;
            particles.push(new Particle(x, y, vx, vy, color, size, life, decay, Math.random() > 0.5));
        }
    }

    function spawnTrailParticles(x, y, count, color = "rgba(255, 255, 255, 0.3)") {
        for (let i = 0; i < count; i++) {
            const vx = (Math.random() - 0.5) * 0.5;
            const vy = (Math.random() - 0.5) * 0.5;
            const size = 1 + Math.random() * 2;
            const life = 0.5;
            const decay = 0.04;
            particles.push(new Particle(x, y, vx, vy, color, size, life, decay));
        }
    }

    function triggerScreenShake(intensity, duration) {
        screenShakeIntensity = intensity;
        screenShakeTimer = duration;
    }

    // --- MURS & COLLISIONS ---
    class Wall {
        constructor(x, y, w, h) {
            this.x = x;
            this.y = y;
            this.w = w;
            this.h = h;
        }

        draw(ctx, cam) {
            const screenPos = cam.toScreen(this.x, this.y);
            ctx.save();
            ctx.strokeStyle = "#ffffff";
            ctx.lineWidth = 2;
            ctx.shadowBlur = 10;
            ctx.shadowColor = "rgba(255, 255, 255, 0.8)";
            ctx.strokeRect(screenPos.x, screenPos.y, this.w, this.h);
            ctx.restore();
        }
    }

    function checkAABBCollision(x1, y1, r1, x2, y2, w2, h2) {
        const closestX = Math.max(x2, Math.min(x1, x2 + w2));
        const closestY = Math.max(y2, Math.min(y1, y2 + h2));
        const distanceX = x1 - closestX;
        const distanceY = y1 - closestY;
        const distanceSquared = (distanceX * distanceX) + (distanceY * distanceY);
        return distanceSquared < (r1 * r1);
    }

    function handleWallCollisions(entityX, entityY, radius) {
        let newX = entityX;
        let newY = entityY;
        
        for (let wall of walls) {
            if (checkAABBCollision(newX, entityY, radius, wall.x, wall.y, wall.w, wall.h)) {
                const closestX = Math.max(wall.x, Math.min(newX, wall.x + wall.w));
                const overlapX = radius - Math.abs(newX - closestX);
                if (newX < closestX) {
                    newX -= overlapX;
                } else {
                    newX += overlapX;
                }
            }
        }

        for (let wall of walls) {
            if (checkAABBCollision(newX, newY, radius, wall.x, wall.y, wall.w, wall.h)) {
                const closestY = Math.max(wall.y, Math.min(entityY, wall.y + wall.h));
                const overlapY = radius - Math.abs(entityY - closestY);
                if (entityY < closestY) {
                    newY -= overlapY;
                } else {
                    newY += overlapY;
                }
            }
        }

        return { x: newX, y: newY };
    }

    // --- ÉPÉE ---
    class WeaponItem {
        constructor(x, y) {
            this.x = x;
            this.y = y;
            this.radius = 20;
            this.hoverTime = 0;
            this.pickedUp = false;
        }

        update(dt, player) {
            if (this.pickedUp) return;
            this.hoverTime += dt * 3;
            
            const dist = Math.hypot(this.x - player.x, this.y - player.y);
            if (dist < player.radius + this.radius) {
                this.pickedUp = true;
                player.hasSword = true;
                player.objective = "ÉLIMINER LES MUTANTS ET S'ÉCHAPPER";
                const objText = document.getElementById("objectiveText");
                if (objText) objText.innerText = player.objective;
                spawnImpactParticles(this.x, this.y, 25, "#ffffff");
                triggerScreenShake(4, 0.2);
            }
        }

        draw(ctx, cam) {
            if (this.pickedUp) return;
            
            const screenPos = cam.toScreen(this.x, this.y);
            const yOffset = Math.sin(this.hoverTime) * 6;
            
            ctx.save();
            ctx.strokeStyle = "#ffffff";
            ctx.lineWidth = 2;
            ctx.shadowBlur = 15;
            ctx.shadowColor = "rgba(255, 255, 255, 0.8)";
            
            ctx.translate(screenPos.x, screenPos.y + yOffset);
            ctx.rotate(-Math.PI / 4);
            
            ctx.beginPath();
            ctx.moveTo(0, 0);
            ctx.lineTo(0, -18);
            ctx.moveTo(-6, -5);
            ctx.lineTo(6, -5);
            ctx.moveTo(0, -5);
            ctx.lineTo(0, 3);
            ctx.stroke();
            
            ctx.strokeStyle = "rgba(255,255,255,0.15)";
            ctx.beginPath();
            ctx.arc(0, -8, 16, 0, Math.PI * 2);
            ctx.stroke();
            
            ctx.restore();
        }
    }

    // --- PORTAIL ---
    class ExitPortal {
        constructor(x, y) {
            this.x = x;
            this.y = y;
            this.radius = 35;
            this.angle = 0;
        }

        update(dt, player) {
            this.angle += dt * 1.5;
            
            if (Math.random() < 0.15) {
                const a = Math.random() * Math.PI * 2;
                const r = this.radius * Math.random();
                const px = this.x + Math.cos(a) * r;
                const py = this.y + Math.sin(a) * r;
                particles.push(new Particle(px, py, 0, -0.5 - Math.random() * 0.5, "#ffffff", 1 + Math.random(), 0.8, 0.03));
            }

            const dist = Math.hypot(this.x - player.x, this.y - player.y);
            if (dist < player.radius + this.radius - 10) {
                setGameState("VICTORY");
                spawnImpactParticles(this.x, this.y, 40, "#ffffff");
            }
        }

        draw(ctx, cam) {
            const screenPos = cam.toScreen(this.x, this.y);
            
            ctx.save();
            ctx.strokeStyle = "#ffffff";
            ctx.shadowBlur = 20;
            ctx.shadowColor = "rgba(255, 255, 255, 0.9)";
            
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.arc(screenPos.x, screenPos.y, this.radius, this.angle, this.angle + Math.PI * 1.6);
            ctx.stroke();

            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.arc(screenPos.x, screenPos.y, this.radius - 10, -this.angle * 1.3, -this.angle * 1.3 + Math.PI * 1.4);
            ctx.stroke();

            ctx.fillStyle = "#ffffff";
            ctx.beginPath();
            ctx.arc(screenPos.x, screenPos.y, 6 + Math.sin(this.angle * 4) * 2, 0, Math.PI * 2);
            ctx.fill();

            ctx.strokeStyle = "rgba(255,255,255,0.3)";
            ctx.lineWidth = 1;
            for (let i = 0; i < 4; i++) {
                const a = this.angle + (i * Math.PI / 2);
                ctx.beginPath();
                ctx.moveTo(screenPos.x + Math.cos(a) * (this.radius + 5), screenPos.y + Math.sin(a) * (this.radius + 5));
                ctx.lineTo(screenPos.x + Math.cos(a) * (this.radius + 12), screenPos.y + Math.sin(a) * (this.radius + 12));
                ctx.stroke();
            }
            
            ctx.restore();
        }
    }

    // --- JOUEUR ---
    class Player {
        constructor(x, y) {
            this.x = x;
            this.y = y;
            this.radius = 16;
            this.speed = 175;
            
            this.maxHp = 100;
            this.hp = 100;
            this.hasSword = false;
            this.objective = "EXPLORER ET SURVIVRE";
            
            this.lookAngle = 0;
            this.runCycle = 0;
            this.isMoving = false;
            this.bobTime = 0;
            this.isDead = false;
            
            this.punchLeftTimer = 0;
            this.punchRightTimer = 0;
            this.punchDuration = 0.15;
            this.punchSide = "left";
            this.swordSwingTimer = 0;
            this.swordSwingDuration = 0.25;
            this.swordSwingSide = 1;
            
            this.invulnTimer = 0;
            this.lanternActive = true;
        }

        update(dt) {
            if (this.isDead) return;

            if (this.punchLeftTimer > 0) this.punchLeftTimer -= dt;
            if (this.punchRightTimer > 0) this.punchRightTimer -= dt;
            if (this.swordSwingTimer > 0) this.swordSwingTimer -= dt;
            if (this.invulnTimer > 0) this.invulnTimer -= dt;

            let moveX = 0;
            let moveY = 0;

            if (keys['z'] || keys['w'] || keys['arrowup']) moveY -= 1;
            if (keys['s'] || keys['arrowdown']) moveY += 1;
            if (keys['q'] || keys['a'] || keys['arrowleft']) moveX -= 1;
            if (keys['d'] || keys['arrowright']) moveX += 1;

            if (moveX !== 0 || moveY !== 0) {
                const length = Math.hypot(moveX, moveY);
                const currentSpeed = this.speed * dt;
                
                this.x += (moveX / length) * currentSpeed;
                this.y += (moveY / length) * currentSpeed;
                this.isMoving = true;
                this.runCycle += dt * 12;
                
                if (Math.random() < 0.1) {
                    spawnTrailParticles(this.x, this.y + 15, 1, "rgba(255,255,255,0.15)");
                }
            } else {
                this.isMoving = false;
                this.bobTime += dt * 3;
            }

            const posAfterCollision = handleWallCollisions(this.x, this.y, this.radius);
            this.x = posAfterCollision.x;
            this.y = posAfterCollision.y;

            const screenPos = camera.toScreen(this.x, this.y - 15);
            this.lookAngle = Math.atan2(mouse.y - screenPos.y, mouse.x - screenPos.x);

            if (mouse.clickLeft || mouse.clickRight) {
                if (this.hasSword) {
                    if (this.swordSwingTimer <= 0) {
                        this.swordSwingTimer = this.swordSwingDuration;
                        this.swordSwingSide = -this.swordSwingSide;
                        this.performSwordAttack();
                    }
                } else {
                    if (this.punchLeftTimer <= 0 && this.punchRightTimer <= 0) {
                        if (this.punchSide === "left") {
                            this.punchLeftTimer = this.punchDuration;
                            this.punchSide = "right";
                            this.performFistPunch("left");
                        } else {
                            this.punchRightTimer = this.punchDuration;
                            this.punchSide = "left";
                            this.performFistPunch("right");
                        }
                    }
                }
                mouse.clickLeft = false;
                mouse.clickRight = false;
            }

            if (keys['f']) {
                this.lanternActive = !this.lanternActive;
                keys['f'] = false;
                spawnImpactParticles(this.x, this.y - 20, 5, "rgba(255,255,255,0.4)");
            }
        }

        takeDamage(amount, sourceX, sourceY) {
            if (this.isDead || this.invulnTimer > 0) return;

            this.hp = Math.max(0, this.hp - amount);
            this.invulnTimer = 0.5;
            
            if (hpBar) hpBar.style.width = `${this.hp}%`;
            
            const angle = Math.atan2(this.y - sourceY, this.x - sourceX);
            this.x += Math.cos(angle) * 20;
            this.y += Math.sin(angle) * 20;
            const posAfterCollision = handleWallCollisions(this.x, this.y, this.radius);
            this.x = posAfterCollision.x;
            this.y = posAfterCollision.y;

            triggerScreenShake(8, 0.25);
            spawnImpactParticles(this.x, this.y - 15, 15, "#ff3333");

            if (this.hp <= 0) {
                this.isDead = true;
                spawnImpactParticles(this.x, this.y - 15, 35, "#ff3333");
                setTimeout(() => setGameState("GAMEOVER"), 1000);
            }
        }

        performFistPunch(side) {
            const punchDist = 32;
            const impactX = this.x + Math.cos(this.lookAngle) * punchDist;
            const impactY = this.y - 15 + Math.sin(this.lookAngle) * punchDist;
            
            spawnImpactParticles(impactX, impactY, 3, "rgba(255,255,255,0.5)");

            let hitSomething = false;
            for (let enemy of enemies) {
                const dist = Math.hypot(enemy.x - impactX, enemy.y - impactY);
                if (dist < enemy.radius + 10) {
                    enemy.takeDamage(15, this.x, this.y);
                    hitSomething = true;
                }
            }

            if (hitSomething) {
                triggerScreenShake(2, 0.1);
            }
        }

        performSwordAttack() {
            const sweepRange = 65;
            const sweepAngle = Math.PI * 0.8;
            const startArc = this.lookAngle - (sweepAngle / 2) * this.swordSwingSide;
            
            for (let i = 0; i <= 6; i++) {
                const a = startArc + (sweepAngle * (i / 6)) * this.swordSwingSide;
                const px = this.x + Math.cos(a) * sweepRange;
                const py = this.y - 15 + Math.sin(a) * sweepRange;
                particles.push(new Particle(px, py, Math.cos(a)*2, Math.sin(a)*2, "rgba(255,255,255,0.4)", 2, 0.3, 0.05));
            }

            let hitSomething = false;
            for (let enemy of enemies) {
                const angleToEnemy = Math.atan2(enemy.y - (this.y - 15), enemy.x - this.x);
                let diffAngle = angleToEnemy - this.lookAngle;
                
                while (diffAngle < -Math.PI) diffAngle += Math.PI * 2;
                while (diffAngle > Math.PI) diffAngle -= Math.PI * 2;

                const dist = Math.hypot(enemy.x - this.x, enemy.y - (this.y - 15));
                if (dist < sweepRange + enemy.radius && Math.abs(diffAngle) < sweepAngle / 2) {
                    enemy.takeDamage(40, this.x, this.y);
                    hitSomething = true;
                }
            }

            if (hitSomething) {
                triggerScreenShake(4, 0.12);
            }
        }

        draw(ctx, cam) {
            if (this.isDead) return;

            const screenPos = cam.toScreen(this.x, this.y);
            
            ctx.save();
            ctx.strokeStyle = "#ffffff";
            ctx.lineWidth = 2.5;
            ctx.lineCap = "round";
            ctx.lineJoin = "round";
            
            ctx.shadowBlur = this.invulnTimer > 0 ? 20 : 10;
            ctx.shadowColor = this.invulnTimer > 0 ? "rgba(255, 51, 51, 0.8)" : "rgba(255, 255, 255, 0.8)";
            
            if (this.invulnTimer > 0 && Math.floor(Date.now() / 50) % 2 === 0) {
                ctx.strokeStyle = "#ff5555";
            }

            const bob = this.isMoving ? 0 : Math.sin(this.bobTime) * 1.2;
            const footHeightY = screenPos.y;
            const hipsY = screenPos.y - 18 + bob;
            const neckY = screenPos.y - 36 + bob;
            const headY = screenPos.y - 46 + bob;
            
            let leftFootX, leftFootY, rightFootX, rightFootY;
            if (this.isMoving) {
                const leftAngle = this.runCycle;
                const rightAngle = this.runCycle + Math.PI;
                
                leftFootX = screenPos.x + Math.sin(leftAngle) * 12;
                leftFootY = footHeightY - Math.max(0, Math.cos(leftAngle) * 4);
                
                rightFootX = screenPos.x + Math.sin(rightAngle) * 12;
                rightFootY = footHeightY - Math.max(0, Math.cos(rightAngle) * 4);
            } else {
                leftFootX = screenPos.x - 6;
                leftFootY = footHeightY;
                rightFootX = screenPos.x + 6;
                rightFootY = footHeightY;
            }

            ctx.beginPath();
            ctx.moveTo(screenPos.x - 3, hipsY);
            ctx.lineTo(leftFootX, leftFootY);
            ctx.stroke();

            ctx.beginPath();
            ctx.moveTo(screenPos.x + 3, hipsY);
            ctx.lineTo(rightFootX, rightFootY);
            ctx.stroke();

            ctx.beginPath();
            ctx.moveTo(screenPos.x, hipsY);
            ctx.lineTo(screenPos.x, neckY);
            ctx.stroke();

            ctx.beginPath();
            ctx.arc(screenPos.x, headY, 7, 0, Math.PI * 2);
            ctx.stroke();
            
            const eyeRadius = 1.2;
            const eyeDist = 3.5;
            const eyeOffsetAngle = 0.4;
            
            const leftEyeX = screenPos.x + Math.cos(this.lookAngle - eyeOffsetAngle) * eyeDist;
            const leftEyeY = headY + Math.sin(this.lookAngle - eyeOffsetAngle) * eyeDist;
            const rightEyeX = screenPos.x + Math.cos(this.lookAngle + eyeOffsetAngle) * eyeDist;
            const rightEyeY = headY + Math.sin(this.lookAngle + eyeOffsetAngle) * eyeDist;
            
            ctx.fillStyle = "#ffffff";
            ctx.beginPath();
            ctx.arc(leftEyeX, leftEyeY, eyeRadius, 0, Math.PI * 2);
            ctx.arc(rightEyeX, rightEyeY, eyeRadius, 0, Math.PI * 2);
            ctx.fill();

            const armLength = 16;
            const shoulderLX = screenPos.x - 4;
            const shoulderRX = screenPos.x + 4;

            if (this.hasSword) {
                let handX, handY;
                
                if (this.swordSwingTimer > 0) {
                    const pct = (this.swordSwingDuration - this.swordSwingTimer) / this.swordSwingDuration;
                    const swingAngle = this.lookAngle + (-Math.PI / 2 + Math.PI * pct) * this.swordSwingSide;
                    
                    handX = screenPos.x + Math.cos(swingAngle) * armLength;
                    handY = neckY + Math.sin(swingAngle) * armLength;
                    
                    ctx.beginPath();
                    ctx.moveTo(shoulderLX, neckY + 2);
                    ctx.lineTo(handX, handY);
                    ctx.moveTo(shoulderRX, neckY + 2);
                    ctx.lineTo(handX, handY);
                    ctx.stroke();

                    ctx.save();
                    ctx.translate(handX, handY);
                    ctx.rotate(swingAngle + Math.PI/4 * this.swordSwingSide);
                    ctx.lineWidth = 2.5;
                    
                    ctx.beginPath();
                    ctx.moveTo(0, 0);
                    ctx.lineTo(0, -32);
                    ctx.moveTo(-9, -7);
                    ctx.lineTo(9, -7);
                    ctx.moveTo(0, -7);
                    ctx.lineTo(0, 3);
                    ctx.stroke();
                    ctx.restore();
                } else {
                    const guardAngle = this.lookAngle - 0.5;
                    handX = screenPos.x + Math.cos(guardAngle) * (armLength - 2);
                    handY = neckY + Math.sin(guardAngle) * (armLength - 2);
                    
                    ctx.beginPath();
                    ctx.moveTo(shoulderLX, neckY + 2);
                    ctx.lineTo(handX, handY);
                    ctx.moveTo(shoulderRX, neckY + 2);
                    ctx.lineTo(handX, handY);
                    ctx.stroke();

                    ctx.save();
                    ctx.translate(handX, handY);
                    ctx.rotate(this.lookAngle + 0.3);
                    ctx.beginPath();
                    ctx.moveTo(0, 0);
                    ctx.lineTo(0, -28);
                    ctx.moveTo(-7, -5);
                    ctx.lineTo(7, -5);
                    ctx.moveTo(0, -5);
                    ctx.lineTo(0, 2);
                    ctx.stroke();
                    ctx.restore();
                }
            } else {
                let leftHandX, leftHandY, rightHandX, rightHandY;

                if (this.punchLeftTimer > 0) {
                    const pct = this.punchLeftTimer / this.punchDuration;
                    const extension = armLength + Math.sin(pct * Math.PI) * 16;
                    leftHandX = shoulderLX + Math.cos(this.lookAngle - 0.3) * extension;
                    leftHandY = neckY + Math.sin(this.lookAngle - 0.3) * extension;
                } else {
                    leftHandX = shoulderLX + Math.cos(this.lookAngle - 0.6) * (armLength - 4);
                    leftHandY = neckY + Math.sin(this.lookAngle - 0.6) * (armLength - 4);
                }

                if (this.punchRightTimer > 0) {
                    const pct = this.punchRightTimer / this.punchDuration;
                    const extension = armLength + Math.sin(pct * Math.PI) * 16;
                    rightHandX = shoulderRX + Math.cos(this.lookAngle + 0.3) * extension;
                    rightHandY = neckY + Math.sin(this.lookAngle + 0.3) * extension;
                } else {
                    rightHandX = shoulderRX + Math.cos(this.lookAngle + 0.6) * (armLength - 4);
                    rightHandY = neckY + Math.sin(this.lookAngle + 0.6) * (armLength - 4);
                }

                ctx.beginPath();
                ctx.moveTo(shoulderLX, neckY + 2);
                ctx.lineTo(leftHandX, leftHandY);
                ctx.stroke();

                ctx.beginPath();
                ctx.moveTo(shoulderRX, neckY + 2);
                ctx.lineTo(rightHandX, rightHandY);
                ctx.stroke();

                ctx.fillStyle = "#ffffff";
                ctx.beginPath();
                ctx.arc(leftHandX, leftHandY, 2.5, 0, Math.PI * 2);
                ctx.arc(rightHandX, rightHandY, 2.5, 0, Math.PI * 2);
                ctx.fill();
            }

            ctx.restore();
        }
    }

    // --- ENNEMI ---
    class Enemy {
        constructor(x, y, isBoss = false) {
            this.x = x;
            this.y = y;
            this.isBoss = isBoss;
            
            this.radius = isBoss ? 28 : 15;
            this.speed = isBoss ? 100 : 120;
            this.maxHp = isBoss ? 200 : 35;
            this.hp = this.maxHp;
            
            this.state = "SLEEPING";
            this.lookAngle = Math.random() * Math.PI * 2;
            this.detectionRadius = isBoss ? 280 : 200;
            
            this.walkCycle = Math.random() * 100;
            this.stunTimer = 0;
            this.bobTime = Math.random() * 100;
            this.swipeTimer = 0;
            this.swipeDuration = 0.2;
        }

        update(dt, player) {
            if (player.isDead) return;

            if (this.stunTimer > 0) {
                this.stunTimer -= dt;
                if (this.stunTimer <= 0) this.state = "CHASING";
            }
            if (this.swipeTimer > 0) this.swipeTimer -= dt;

            if (this.state === "STUNNED") {
                if (Math.random() < 0.2) {
                    spawnTrailParticles(this.x, this.y + 10, 1, "rgba(255, 51, 51, 0.4)");
                }
                const posAfterCollision = handleWallCollisions(this.x, this.y, this.radius);
                this.x = posAfterCollision.x;
                this.y = posAfterCollision.y;
                return;
            }

            const distToPlayer = Math.hypot(player.x - this.x, player.y - this.y);

            if (this.state === "SLEEPING") {
                const detectRange = player.lanternActive ? this.detectionRadius : this.detectionRadius * 0.4;
                if (distToPlayer < detectRange) {
                    this.state = "ALERT";
                    this.stunTimer = 0.4;
                    spawnImpactParticles(this.x, this.y - 25, 6, "#ff3333");
                    triggerScreenShake(1.5, 0.1);
                }
                this.bobTime += dt * 2;
            } 
            else if (this.state === "ALERT") {
                this.lookAngle = Math.atan2(player.y - this.y, player.x - this.x);
                if (this.stunTimer <= 0) {
                    this.state = "CHASING";
                }
            } 
            else if (this.state === "CHASING") {
                this.lookAngle = Math.atan2(player.y - this.y, player.x - this.x);
                
                const vx = Math.cos(this.lookAngle) * this.speed * dt;
                const vy = Math.sin(this.lookAngle) * this.speed * dt;
                
                this.x += vx;
                this.y += vy;
                this.walkCycle += dt * (this.isBoss ? 8 : 13);

                const posAfterCollision = handleWallCollisions(this.x, this.y, this.radius);
                this.x = posAfterCollision.x;
                this.y = posAfterCollision.y;

                const attackRange = this.radius + player.radius + 8;
                if (distToPlayer < attackRange) {
                    if (this.swipeTimer <= 0) {
                        this.swipeTimer = this.swipeDuration;
                        player.takeDamage(this.isBoss ? 25 : 12, this.x, this.y);
                    }
                }
            }
        }

        takeDamage(amount, sourceX, sourceY) {
            this.hp -= amount;
            this.state = "STUNNED";
            this.stunTimer = 0.25;
            
            const angle = Math.atan2(this.y - sourceY, this.x - sourceX);
            const knock = this.isBoss ? 15 : 35;
            this.x += Math.cos(angle) * knock;
            this.y += Math.sin(angle) * knock;
            
            const posAfterCollision = handleWallCollisions(this.x, this.y, this.radius);
            this.x = posAfterCollision.x;
            this.y = posAfterCollision.y;

            spawnImpactParticles(this.x, this.y - 12, 10, "#aa0000");
            spawnImpactParticles(this.x, this.y - 12, 5, "#ff3333");

            if (this.hp <= 0) {
                spawnImpactParticles(this.x, this.y - 12, this.isBoss ? 45 : 20, "#880000");
                spawnImpactParticles(this.x, this.y - 12, this.isBoss ? 20 : 10, "#ffffff");
                enemies = enemies.filter(e => e !== this);
                triggerScreenShake(this.isBoss ? 7 : 3, 0.15);
            }
        }

        draw(ctx, cam) {
            const screenPos = cam.toScreen(this.x, this.y);
            
            ctx.save();
            ctx.strokeStyle = "#ff4444";
            ctx.lineWidth = this.isBoss ? 3.5 : 2.2;
            ctx.lineCap = "round";
            ctx.lineJoin = "round";
            
            ctx.shadowBlur = this.state === "SLEEPING" ? 4 : 12;
            ctx.shadowColor = "rgba(255, 51, 51, 0.8)";
            
            if (this.state === "STUNNED") {
                ctx.strokeStyle = "#ffffff";
                ctx.shadowColor = "rgba(255, 255, 255, 0.8)";
            }

            const isChasing = this.state === "CHASING";
            const bob = Math.sin(isChasing ? this.walkCycle * 0.8 : this.bobTime) * (this.isBoss ? 2 : 1.5);
            
            const groundY = screenPos.y;
            const hipsY = groundY - (this.isBoss ? 25 : 12) + bob;
            
            const forwardX = Math.cos(this.lookAngle) * (this.isBoss ? 15 : 8);
            const forwardY = Math.sin(this.lookAngle) * (this.isBoss ? 5 : 2);
            
            const neckX = screenPos.x + forwardX;
            const neckY = groundY - (this.isBoss ? 45 : 24) + bob + forwardY;
            
            const headX = neckX + Math.cos(this.lookAngle) * (this.isBoss ? 10 : 6);
            const headY = neckY - (this.isBoss ? 10 : 6);

            let leftFootX, leftFootY, rightFootX, rightFootY;
            if (isChasing) {
                const leftAngle = this.walkCycle;
                const rightAngle = this.walkCycle + Math.PI + 0.5;
                
                leftFootX = screenPos.x + Math.sin(leftAngle) * (this.isBoss ? 16 : 9);
                leftFootY = groundY - Math.max(0, Math.cos(leftAngle) * 6);
                
                rightFootX = screenPos.x + Math.sin(rightAngle) * (this.isBoss ? 14 : 8);
                rightFootY = groundY - Math.max(0, Math.cos(rightAngle) * 5);
            } else {
                leftFootX = screenPos.x - (this.isBoss ? 12 : 5);
                leftFootY = groundY;
                rightFootX = screenPos.x + (this.isBoss ? 12 : 5);
                rightFootY = groundY;
            }

            const kneeLX = (screenPos.x - 4 + leftFootX) / 2 - (this.isBoss ? 6 : 3);
            ctx.beginPath();
            ctx.moveTo(screenPos.x - 3, hipsY);
            ctx.lineTo(kneeLX, (hipsY + leftFootY) / 2);
            ctx.lineTo(leftFootX, leftFootY);
            ctx.stroke();

            const kneeRX = (screenPos.x + 4 + rightFootX) / 2 + (this.isBoss ? 6 : 3);
            ctx.beginPath();
            ctx.moveTo(screenPos.x + 3, hipsY);
            ctx.lineTo(kneeRX, (hipsY + rightFootY) / 2);
            ctx.lineTo(rightFootX, rightFootY);
            ctx.stroke();

            ctx.beginPath();
            ctx.moveTo(screenPos.x, hipsY);
            ctx.quadraticCurveTo(screenPos.x - forwardX * 0.5, (hipsY + neckY) / 2, neckX, neckY);
            ctx.stroke();

            ctx.beginPath();
            ctx.arc(headX, headY, this.isBoss ? 11 : 5, 0, Math.PI * 2);
            ctx.stroke();

            if (this.state !== "SLEEPING") {
                const eyeX = headX + Math.cos(this.lookAngle) * (this.isBoss ? 7 : 3);
                const eyeY = headY + Math.sin(this.lookAngle) * (this.isBoss ? 7 : 3);
                ctx.fillStyle = "#ff0000";
                ctx.beginPath();
                ctx.arc(eyeX, eyeY, this.isBoss ? 3 : 1.5, 0, Math.PI * 2);
                ctx.fill();
            }

            const armLength = this.isBoss ? 32 : 16;
            let leftHandX, leftHandY, rightHandX, rightHandY;

            if (this.swipeTimer > 0) {
                const pct = this.swipeTimer / this.swipeDuration;
                const extension = armLength + Math.sin(pct * Math.PI) * (this.isBoss ? 20 : 10);
                
                leftHandX = neckX + Math.cos(this.lookAngle - 0.2) * extension;
                leftHandY = neckY + Math.sin(this.lookAngle - 0.2) * extension;
                rightHandX = neckX + Math.cos(this.lookAngle + 0.2) * extension;
                rightHandY = neckY + Math.sin(this.lookAngle + 0.2) * extension;
            } else {
                leftHandX = neckX - (this.isBoss ? 15 : 6) + Math.cos(this.lookAngle + 0.3) * (armLength * 0.6);
                leftHandY = neckY + (this.isBoss ? 20 : 12) + Math.sin(this.lookAngle + 0.3) * (armLength * 0.4);
                
                rightHandX = neckX + (this.isBoss ? 15 : 6) + Math.cos(this.lookAngle - 0.3) * (armLength * 0.6);
                rightHandY = neckY + (this.isBoss ? 22 : 13) + Math.sin(this.lookAngle - 0.3) * (armLength * 0.4);
            }

            ctx.beginPath();
            ctx.moveTo(neckX - 3, neckY + 2);
            ctx.lineTo(leftHandX, leftHandY);
            ctx.moveTo(neckX + 3, neckY + 2);
            ctx.lineTo(rightHandX, rightHandY);
            ctx.stroke();

            ctx.strokeStyle = "#ffffff";
            ctx.lineWidth = 1;
            ctx.shadowBlur = 4;
            ctx.shadowColor = "#ffffff";
            for (let i = 0; i < 3; i++) {
                const spread = (i - 1) * 3;
                ctx.beginPath();
                ctx.moveTo(leftHandX, leftHandY);
                ctx.lineTo(leftHandX + Math.cos(this.lookAngle + 0.2)*4 + spread*Math.cos(this.lookAngle+Math.PI/2)*0.3, leftHandY + Math.sin(this.lookAngle + 0.2)*4 + spread*Math.sin(this.lookAngle+Math.PI/2)*0.3);
                ctx.stroke();
                
                ctx.beginPath();
                ctx.moveTo(rightHandX, rightHandY);
                ctx.lineTo(rightHandX + Math.cos(this.lookAngle - 0.2)*4 + spread*Math.cos(this.lookAngle-Math.PI/2)*0.3, rightHandY + Math.sin(this.lookAngle - 0.2)*4 + spread*Math.sin(this.lookAngle-Math.PI/2)*0.3);
                ctx.stroke();
            }

            if (this.hp < this.maxHp) {
                const barW = this.isBoss ? 40 : 20;
                const barH = 3;
                const barX = screenPos.x - barW / 2;
                const barY = headY - 12;
                
                ctx.fillStyle = "rgba(0,0,0,0.6)";
                ctx.fillRect(barX, barY, barW, barH);
                
                ctx.fillStyle = "#ff3333";
                ctx.fillRect(barX, barY, barW * (this.hp / this.maxHp), barH);
                
                ctx.strokeStyle = "rgba(255,255,255,0.2)";
                ctx.lineWidth = 0.5;
                ctx.strokeRect(barX, barY, barW, barH);
            }

            ctx.restore();
        }
    }

    // --- CONSTRUIRE CARTE ---
    function buildMap() {
        walls = [];
        enemies = [];
        exitPortal = null;
        swordItem = null;

        for (let r = 0; r < MAP_ROWS; r++) {
            for (let c = 0; c < MAP_COLS; c++) {
                const tile = MAP_LAYOUT[r][c];
                const x = c * TILE_SIZE;
                const y = r * TILE_SIZE;

                if (tile === 1) {
                    walls.push(new Wall(x, y, TILE_SIZE, TILE_SIZE));
                } else {
                    if (tile === 'E') {
                        spawnPoint = { x: x + TILE_SIZE / 2, y: y + TILE_SIZE / 2 + 15 };
                    } else if (tile === 'X') {
                        exitPortal = new ExitPortal(x + TILE_SIZE / 2, y + TILE_SIZE / 2);
                    } else if (tile === 'W') {
                        swordItem = new WeaponItem(x + TILE_SIZE / 2, y + TILE_SIZE / 2);
                    } else if (tile === 'M') {
                        enemies.push(new Enemy(x + TILE_SIZE / 2, y + TILE_SIZE / 2));
                    }
                }
            }
        }

        if (exitPortal) {
            enemies.push(new Enemy(exitPortal.x - 120, exitPortal.y, true));
        }
    }

    // --- DESSIN CARTE ---
    function drawWireframeMap(ctx, cam) {
        ctx.save();
        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 2.5;
        ctx.shadowBlur = 10;
        ctx.shadowColor = "rgba(255, 255, 255, 0.7)";
        
        for (let r = 0; r < MAP_ROWS; r++) {
            for (let c = 0; c < MAP_COLS; c++) {
                if (MAP_LAYOUT[r][c] !== 1) continue;

                const x = c * TILE_SIZE;
                const y = r * TILE_SIZE;
                const screenPos = cam.toScreen(x, y);

                if (r > 0 && MAP_LAYOUT[r-1][c] !== 1) {
                    ctx.beginPath();
                    ctx.moveTo(screenPos.x, screenPos.y);
                    ctx.lineTo(screenPos.x + TILE_SIZE, screenPos.y);
                    ctx.stroke();
                }
                if (r < MAP_ROWS - 1 && MAP_LAYOUT[r+1][c] !== 1) {
                    ctx.beginPath();
                    ctx.moveTo(screenPos.x, screenPos.y + TILE_SIZE);
                    ctx.lineTo(screenPos.x + TILE_SIZE, screenPos.y + TILE_SIZE);
                    ctx.stroke();
                }
                if (c > 0 && MAP_LAYOUT[r][c-1] !== 1) {
                    ctx.beginPath();
                    ctx.moveTo(screenPos.x, screenPos.y);
                    ctx.lineTo(screenPos.x, screenPos.y + TILE_SIZE);
                    ctx.stroke();
                }
                if (c < MAP_COLS - 1 && MAP_LAYOUT[r][c+1] !== 1) {
                    ctx.beginPath();
                    ctx.moveTo(screenPos.x + TILE_SIZE, screenPos.y);
                    ctx.lineTo(screenPos.x + TILE_SIZE, screenPos.y + TILE_SIZE);
                    ctx.stroke();
                }
            }
        }
        ctx.restore();
    }

    // --- MASQUE LUMIÈRE ---
    function drawLightingMask(ctx, cam, player) {
        if (!player.lanternActive) {
            ctx.save();
            const maskCanvas = document.createElement("canvas");
            maskCanvas.width = canvas.width;
            maskCanvas.height = canvas.height;
            const maskCtx = maskCanvas.getContext("2d");
            
            maskCtx.fillStyle = "black";
            maskCtx.fillRect(0, 0, canvas.width, canvas.height);
            
            const pScreen = cam.toScreen(player.x, player.y - 15);
            maskCtx.globalCompositeOperation = "destination-out";
            maskCtx.beginPath();
            maskCtx.arc(pScreen.x, pScreen.y, 40, 0, Math.PI * 2);
            maskCtx.fill();
            
            ctx.drawImage(maskCanvas, 0, 0);
            ctx.restore();
            return;
        }

        const time = Date.now() * 0.001;
        const flicker = Math.sin(time * 25) * 3 + Math.cos(time * 40) * 1.5 + (Math.random() - 0.5) * 2;
        const baseRadius = 220;
        const radius = Math.max(80, baseRadius + flicker);

        ctx.save();
        
        const tempCanvas = document.createElement("canvas");
        tempCanvas.width = canvas.width;
        tempCanvas.height = canvas.height;
        const tempCtx = tempCanvas.getContext("2d");

        tempCtx.fillStyle = "rgba(0, 0, 0, 0.96)";
        tempCtx.fillRect(0, 0, canvas.width, canvas.height);

        const playerScreen = cam.toScreen(player.x, player.y - 15);

        const gradient = tempCtx.createRadialGradient(
            playerScreen.x, playerScreen.y, 10,
            playerScreen.x, playerScreen.y, radius
        );
        gradient.addColorStop(0, "rgba(0, 0, 0, 1)");
        gradient.addColorStop(0.3, "rgba(0, 0, 0, 0.85)");
        gradient.addColorStop(0.6, "rgba(0, 0, 0, 0.4)");
        gradient.addColorStop(0.85, "rgba(0, 0, 0, 0.1)");
        gradient.addColorStop(1, "rgba(0, 0, 0, 0)");

        tempCtx.globalCompositeOperation = "destination-out";
        tempCtx.fillStyle = gradient;
        tempCtx.beginPath();
        tempCtx.arc(playerScreen.x, playerScreen.y, radius, 0, Math.PI * 2);
        tempCtx.fill();

        ctx.drawImage(tempCanvas, 0, 0);
        ctx.restore();
    }

    // --- CURSEUR VISÉE ---
    function drawCustomCrosshair(ctx) {
        ctx.save();
        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 1.5;
        ctx.shadowBlur = 10;
        ctx.shadowColor = "rgba(255, 255, 255, 0.8)";
        
        ctx.beginPath();
        ctx.arc(mouse.x, mouse.y, 5, 0, Math.PI * 2);
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(mouse.x - 10, mouse.y);
        ctx.lineTo(mouse.x - 7, mouse.y);
        ctx.moveTo(mouse.x + 7, mouse.y);
        ctx.lineTo(mouse.x + 10, mouse.y);
        ctx.moveTo(mouse.x, mouse.y - 10);
        ctx.lineTo(mouse.x, mouse.y - 7);
        ctx.moveTo(mouse.x, mouse.y + 7);
        ctx.lineTo(mouse.x, mouse.y + 10);
        ctx.stroke();
        
        ctx.restore();
    }

    // --- BOUCLE DE JEU ---
    function gameLoop(timestamp) {
        const dt = Math.min(0.1, (timestamp - lastTime) / 1000);
        lastTime = timestamp;

        let shakeOffsetX = 0;
        let shakeOffsetY = 0;
        if (screenShakeTimer > 0) {
            screenShakeTimer -= dt;
            shakeOffsetX = (Math.random() - 0.5) * screenShakeIntensity;
            shakeOffsetY = (Math.random() - 0.5) * screenShakeIntensity;
            if (screenShakeTimer <= 0) {
                screenShakeIntensity = 0;
            }
        }

        if (gameState === "PLAYING" && player) {
            player.update(dt);
            camera.update(player.x, player.y);

            for (let enemy of enemies) {
                enemy.update(dt, player);
            }

            if (swordItem) swordItem.update(dt, player);
            if (exitPortal) exitPortal.update(dt, player);

            for (let particle of particles) {
                particle.update(dt);
            }
            particles = particles.filter(p => p.life > 0);
        }

        ctx.fillStyle = "#000000";
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.save();
        ctx.translate(shakeOffsetX, shakeOffsetY);

        drawWireframeMap(ctx, camera);

        if (swordItem) swordItem.draw(ctx, camera);
        if (exitPortal) exitPortal.draw(ctx, camera);

        for (let particle of particles) {
            particle.draw(ctx, camera);
        }

        for (let enemy of enemies) {
            enemy.draw(ctx, camera);
        }

        if (player) player.draw(ctx, camera);

        if (gameState === "PLAYING" && player) {
            drawLightingMask(ctx, camera, player);
        }

        ctx.restore();

        if (gameState === "PLAYING") {
            drawCustomCrosshair(ctx);
        }

        requestAnimationFrame(gameLoop);
    }

    // --- GESTION ÉTATS ---
    function setGameState(newState) {
        gameState = newState;
        console.log("Nouvel état de jeu :", newState);

        Object.values(screens).forEach(screen => {
            if (screen) screen.classList.remove("active");
        });
        if (hud) hud.classList.remove("active");
        if (instructions) instructions.classList.remove("active");

        if (newState === "MENU") {
            if (screens.MENU) screens.MENU.classList.add("active");
        } 
        else if (newState === "PLAYING") {
            if (hud) hud.classList.add("active");
            if (instructions) instructions.classList.add("active");
            
            buildMap();
            player = new Player(spawnPoint.x, spawnPoint.y);
            if (hpBar) hpBar.style.width = "100%";
            
            const objText = document.getElementById("objectiveText");
            if (objText && player) objText.innerText = player.objective;
            
            particles = [];
            triggerScreenShake(3, 0.15);
        } 
        else if (newState === "GAMEOVER") {
            if (screens.GAMEOVER) screens.GAMEOVER.classList.add("active");
        } 
        else if (newState === "VICTORY") {
            if (screens.VICTORY) screens.VICTORY.classList.add("active");
        }
    }

    // --- ENREGISTREMENT CLICS ---
    if (startBtn) {
        console.log("Bouton Commencer trouvé, liaison de l'événement clic.");
        startBtn.addEventListener("click", () => {
            console.log("Clic détecté sur Commencer !");
            setGameState("PLAYING");
        });
    } else {
        console.error("ERREUR : Bouton startBtn introuvable !");
    }

    if (restartBtn) restartBtn.addEventListener("click", () => setGameState("PLAYING"));
    if (nextLevelBtn) nextLevelBtn.addEventListener("click", () => setGameState("PLAYING"));

    // --- DÉMARRAGE DE LA BOUCLE ---
    requestAnimationFrame((timestamp) => {
        lastTime = timestamp;
        setGameState("MENU");
        requestAnimationFrame(gameLoop);
    });
}

// --- INITIALISATION SÉCURISÉE MULTI-LANCEMENT ---
// Cette section résout définitivement le problème de timing où DOMContentLoaded s'est déjà produit
if (document.readyState === "loading") {
    console.log("DOM toujours en chargement, écoute de DOMContentLoaded...");
    document.addEventListener("DOMContentLoaded", initGame);
} else {
    console.log("DOM déjà chargé. Exécution immédiate de initGame.");
    initGame();
}
