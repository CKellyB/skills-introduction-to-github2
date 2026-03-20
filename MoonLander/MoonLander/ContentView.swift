import SwiftUI

struct ContentView: View {
    @StateObject private var game = GameModel()

    var body: some View {
        ZStack {
            Color.black.ignoresSafeArea()

            switch game.state {
            case .idle:
                TitleView(game: game)
            case .playing:
                GameView(game: game)
            case .landed:
                ResultView(game: game, success: true)
            case .crashed:
                ResultView(game: game, success: false)
            }
        }
        .preferredColorScheme(.dark)
    }
}

// MARK: - Title Screen

struct TitleView: View {
    let game: GameModel

    var body: some View {
        VStack(spacing: 32) {
            Spacer()

            VStack(spacing: 8) {
                Text("🌕")
                    .font(.system(size: 80))
                Text("MOON LANDER")
                    .font(.system(size: 36, weight: .bold, design: .monospaced))
                    .foregroundColor(.white)
                Text("Guide your lander safely to the surface")
                    .font(.system(size: 14, design: .monospaced))
                    .foregroundColor(.gray)
                    .multilineTextAlignment(.center)
            }

            VStack(alignment: .leading, spacing: 10) {
                InstructionRow(icon: "arrow.up", text: "THRUST button — fire main engine")
                InstructionRow(icon: "arrow.left", text: "LEFT / RIGHT — rotate lander")
                InstructionRow(icon: "target", text: "Land on the pad at ≤ 5 m/s")
                InstructionRow(icon: "angle", text: "Keep angle within ±10°")
            }
            .padding()
            .background(Color.white.opacity(0.05))
            .cornerRadius(12)

            Button(action: { game.startGame() }) {
                Text("LAUNCH MISSION")
                    .font(.system(size: 18, weight: .bold, design: .monospaced))
                    .foregroundColor(.black)
                    .padding(.horizontal, 40)
                    .padding(.vertical, 14)
                    .background(Color.green)
                    .cornerRadius(10)
            }

            Spacer()
        }
        .padding(24)
    }
}

struct InstructionRow: View {
    let icon: String
    let text: String

    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: icon)
                .foregroundColor(.yellow)
                .frame(width: 20)
            Text(text)
                .font(.system(size: 13, design: .monospaced))
                .foregroundColor(.white)
        }
    }
}

// MARK: - Game View

struct GameView: View {
    @ObservedObject var game: GameModel

    var body: some View {
        VStack(spacing: 0) {
            HUDView(game: game)
            SpaceView(game: game)
            ControlsView(game: game)
        }
    }
}

// MARK: - HUD

struct HUDView: View {
    @ObservedObject var game: GameModel

    var body: some View {
        HStack(spacing: 16) {
            HUDItem(label: "ALT", value: String(format: "%.0f m", game.altitude))
            HUDItem(label: "V.SPEED", value: String(format: "%.1f m/s", game.velocityY),
                    color: abs(game.velocityY) > GameModel.safeVelocity ? .red : .green)
            HUDItem(label: "H.SPEED", value: String(format: "%.1f m/s", game.velocityX))
            HUDItem(label: "ANGLE", value: String(format: "%.1f°", game.angle),
                    color: abs(game.angle) > GameModel.safeAngle ? .red : .green)
            HUDItem(label: "FUEL",
                    value: String(format: "%.0f%%", game.fuel / GameModel.maxFuel * 100),
                    color: game.fuel < 20 ? .red : game.fuel < 40 ? .yellow : .green)
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 10)
        .background(Color(white: 0.07))
    }
}

struct HUDItem: View {
    let label: String
    let value: String
    var color: Color = .white

    var body: some View {
        VStack(spacing: 2) {
            Text(label)
                .font(.system(size: 9, weight: .medium, design: .monospaced))
                .foregroundColor(.gray)
            Text(value)
                .font(.system(size: 12, weight: .bold, design: .monospaced))
                .foregroundColor(color)
        }
        .frame(maxWidth: .infinity)
    }
}

// MARK: - Space / Lander View

struct SpaceView: View {
    @ObservedObject var game: GameModel

    var body: some View {
        GeometryReader { geo in
            ZStack {
                // Stars background
                StarsView()

                // Moon surface
                MoonSurfaceView(
                    landingPadX: game.landingPadX,
                    landingPadWidth: game.landingPadWidth,
                    width: geo.size.width,
                    height: geo.size.height
                )

                // Lander
                LanderView(thrustLevel: game.thrustLevel, angle: game.angle)
                    .position(
                        x: geo.size.width * game.positionX,
                        y: geo.size.height * game.positionY
                    )
            }
        }
        .background(Color.black)
    }
}

struct StarsView: View {
    let stars: [(CGFloat, CGFloat, CGFloat)] = (0..<80).map { _ in
        (CGFloat.random(in: 0...1),
         CGFloat.random(in: 0...1),
         CGFloat.random(in: 1...3))
    }

    var body: some View {
        GeometryReader { geo in
            ForEach(0..<stars.count, id: \.self) { i in
                Circle()
                    .fill(Color.white.opacity(Double.random(in: 0.4...1.0)))
                    .frame(width: stars[i].2, height: stars[i].2)
                    .position(x: geo.size.width * stars[i].0,
                              y: geo.size.height * stars[i].1)
            }
        }
    }
}

struct MoonSurfaceView: View {
    let landingPadX: Double
    let landingPadWidth: Double
    let width: CGFloat
    let height: CGFloat

    var body: some View {
        let padLeft = CGFloat(landingPadX - landingPadWidth / 2) * width
        let padRight = CGFloat(landingPadX + landingPadWidth / 2) * width
        let surfaceY = height - 40

        Canvas { context, size in
            // Terrain
            var terrain = Path()
            terrain.move(to: CGPoint(x: 0, y: surfaceY + 15))
            terrain.addLine(to: CGPoint(x: padLeft - 20, y: surfaceY + 8))
            terrain.addLine(to: CGPoint(x: padLeft, y: surfaceY))
            terrain.addLine(to: CGPoint(x: padRight, y: surfaceY))
            terrain.addLine(to: CGPoint(x: padRight + 25, y: surfaceY + 12))
            terrain.addLine(to: CGPoint(x: size.width, y: surfaceY + 5))
            terrain.addLine(to: CGPoint(x: size.width, y: size.height))
            terrain.addLine(to: CGPoint(x: 0, y: size.height))
            terrain.closeSubpath()
            context.fill(terrain, with: .color(Color(white: 0.45)))

            // Landing pad
            var pad = Path()
            pad.move(to: CGPoint(x: padLeft, y: surfaceY))
            pad.addLine(to: CGPoint(x: padRight, y: surfaceY))
            pad.addLine(to: CGPoint(x: padRight, y: surfaceY + 4))
            pad.addLine(to: CGPoint(x: padLeft, y: surfaceY + 4))
            context.fill(pad, with: .color(.yellow))

            // Pad markers
            for i in stride(from: padLeft, to: padRight, by: 8) {
                var marker = Path()
                marker.move(to: CGPoint(x: i, y: surfaceY))
                marker.addLine(to: CGPoint(x: i + 4, y: surfaceY))
                context.stroke(marker, with: .color(.black), lineWidth: 2)
            }
        }
    }
}

struct LanderView: View {
    let thrustLevel: Double
    let angle: Double
    @State private var flameScale: CGFloat = 1.0

    var body: some View {
        ZStack {
            // Thrust flame
            if thrustLevel > 0.05 {
                FlameView(thrustLevel: thrustLevel)
                    .offset(y: 18)
                    .scaleEffect(flameScale)
                    .onAppear {
                        withAnimation(.easeInOut(duration: 0.1).repeatForever(autoreverses: true)) {
                            flameScale = 1.2
                        }
                    }
            }

            // Lander body
            LanderBodyView()
        }
        .rotationEffect(.degrees(angle))
    }
}

struct LanderBodyView: View {
    var body: some View {
        ZStack {
            // Legs
            Path { path in
                // Left leg
                path.move(to: CGPoint(x: 0, y: 10))
                path.addLine(to: CGPoint(x: -14, y: 20))
                path.addLine(to: CGPoint(x: -18, y: 20))
                // Right leg
                path.move(to: CGPoint(x: 0, y: 10))
                path.addLine(to: CGPoint(x: 14, y: 20))
                path.addLine(to: CGPoint(x: 18, y: 20))
            }
            .stroke(Color(white: 0.8), lineWidth: 2)

            // Main body
            Capsule()
                .fill(Color(white: 0.75))
                .frame(width: 20, height: 30)

            // Window
            Circle()
                .fill(Color.cyan.opacity(0.8))
                .frame(width: 8, height: 8)
                .offset(y: -3)

            // Engine bell
            Path { path in
                path.move(to: CGPoint(x: -7, y: 12))
                path.addLine(to: CGPoint(x: 7, y: 12))
                path.addLine(to: CGPoint(x: 5, y: 18))
                path.addLine(to: CGPoint(x: -5, y: 18))
                path.closeSubpath()
            }
            .fill(Color(white: 0.5))
        }
        .frame(width: 40, height: 40)
    }
}

struct FlameView: View {
    let thrustLevel: Double

    var body: some View {
        ZStack {
            Ellipse()
                .fill(
                    RadialGradient(
                        colors: [.white, .yellow, .orange, .clear],
                        center: .top,
                        startRadius: 0,
                        endRadius: CGFloat(12 + thrustLevel * 10)
                    )
                )
                .frame(width: 12, height: CGFloat(18 + thrustLevel * 14))
        }
    }
}

// MARK: - Controls

struct ControlsView: View {
    @ObservedObject var game: GameModel

    var body: some View {
        HStack(spacing: 0) {
            // Left rotate
            RotateButton(direction: -1, label: "◀ LEFT", game: game)

            // Thrust
            ThrustButton(game: game)

            // Right rotate
            RotateButton(direction: 1, label: "RIGHT ▶", game: game)
        }
        .frame(height: 100)
        .background(Color(white: 0.07))
    }
}

struct ThrustButton: View {
    @ObservedObject var game: GameModel

    var body: some View {
        ZStack {
            Rectangle()
                .fill(game.thrustLevel > 0 ? Color.orange.opacity(0.4) : Color.white.opacity(0.05))
            VStack(spacing: 4) {
                Image(systemName: "flame.fill")
                    .font(.system(size: 24))
                    .foregroundColor(game.thrustLevel > 0 ? .orange : .gray)
                Text("THRUST")
                    .font(.system(size: 11, weight: .bold, design: .monospaced))
                    .foregroundColor(.white)
            }
        }
        .frame(maxWidth: .infinity)
        .contentShape(Rectangle())
        .gesture(
            DragGesture(minimumDistance: 0)
                .onChanged { _ in game.thrustLevel = 1.0 }
                .onEnded { _ in game.thrustLevel = 0.0 }
        )
    }
}

struct RotateButton: View {
    let direction: Double
    let label: String
    @ObservedObject var game: GameModel

    var body: some View {
        ZStack {
            Rectangle()
                .fill(Color.white.opacity(0.05))
            Text(label)
                .font(.system(size: 12, weight: .bold, design: .monospaced))
                .foregroundColor(.white)
        }
        .frame(maxWidth: .infinity)
        .contentShape(Rectangle())
        .gesture(
            DragGesture(minimumDistance: 0)
                .onChanged { _ in game.rotationInput = direction }
                .onEnded { _ in game.rotationInput = 0.0 }
        )
    }
}

// MARK: - Result Screen

struct ResultView: View {
    let game: GameModel
    let success: Bool

    var body: some View {
        VStack(spacing: 28) {
            Spacer()

            VStack(spacing: 12) {
                Text(success ? "🎉" : "💥")
                    .font(.system(size: 64))
                Text(success ? "SUCCESSFUL LANDING!" : "CRASHED!")
                    .font(.system(size: 28, weight: .bold, design: .monospaced))
                    .foregroundColor(success ? .green : .red)
                    .multilineTextAlignment(.center)
            }

            if success {
                VStack(spacing: 8) {
                    Text("SCORE")
                        .font(.system(size: 14, design: .monospaced))
                        .foregroundColor(.gray)
                    Text("\(game.score)")
                        .font(.system(size: 48, weight: .bold, design: .monospaced))
                        .foregroundColor(.yellow)
                }
                .padding()
                .background(Color.white.opacity(0.05))
                .cornerRadius(12)
            } else {
                VStack(spacing: 6) {
                    Text("Impact speed: \(String(format: "%.1f m/s", sqrt(game.velocityX * game.velocityX + game.velocityY * game.velocityY)))")
                    Text("Angle: \(String(format: "%.1f°", game.angle))")
                }
                .font(.system(size: 14, design: .monospaced))
                .foregroundColor(.gray)
            }

            HStack(spacing: 20) {
                Button(action: { game.startGame() }) {
                    Text("TRY AGAIN")
                        .font(.system(size: 16, weight: .bold, design: .monospaced))
                        .foregroundColor(.black)
                        .padding(.horizontal, 28)
                        .padding(.vertical, 12)
                        .background(Color.green)
                        .cornerRadius(10)
                }

                Button(action: { game.stopGame() }) {
                    Text("MENU")
                        .font(.system(size: 16, weight: .bold, design: .monospaced))
                        .foregroundColor(.white)
                        .padding(.horizontal, 28)
                        .padding(.vertical, 12)
                        .background(Color.white.opacity(0.15))
                        .cornerRadius(10)
                }
            }

            Spacer()
        }
        .padding(24)
    }
}
