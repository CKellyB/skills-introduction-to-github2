import Foundation
import Combine

enum GameState {
    case idle
    case playing
    case landed
    case crashed
}

class GameModel: ObservableObject {
    // Physics constants
    static let gravity: Double = 1.62       // m/s² (Moon gravity)
    static let maxThrust: Double = 4.0      // m/s² (thrust acceleration)
    static let maxFuel: Double = 100.0
    static let fuelBurnRate: Double = 10.0  // units/s at full thrust
    static let safeVelocity: Double = 5.0   // m/s max landing speed
    static let safeAngle: Double = 10.0     // degrees max landing angle

    // Starting conditions
    static let startAltitude: Double = 500.0
    static let startVelocityY: Double = -10.0

    @Published var altitude: Double = startAltitude
    @Published var velocityY: Double = startVelocityY  // negative = falling
    @Published var velocityX: Double = 0.0
    @Published var angle: Double = 0.0     // degrees, 0 = upright
    @Published var angularVelocity: Double = 0.0
    @Published var fuel: Double = maxFuel
    @Published var thrustLevel: Double = 0.0  // 0.0 to 1.0
    @Published var rotationInput: Double = 0.0 // -1 left, +1 right
    @Published var state: GameState = .idle
    @Published var score: Int = 0

    private var timer: AnyCancellable?
    private let tickRate: Double = 1.0 / 60.0  // 60 FPS

    // Lander position on screen (normalized 0-1)
    @Published var positionX: Double = 0.5
    @Published var positionY: Double = 0.1  // starts near top

    // Terrain (landing pad center x in normalized coords)
    let landingPadX: Double = 0.5
    let landingPadWidth: Double = 0.15

    func startGame() {
        altitude = GameModel.startAltitude
        velocityY = GameModel.startVelocityY
        velocityX = 0.0
        angle = 0.0
        angularVelocity = 0.0
        fuel = GameModel.maxFuel
        thrustLevel = 0.0
        rotationInput = 0.0
        positionX = 0.5
        positionY = 0.1
        state = .playing
        score = 0
        startTimer()
    }

    func stopGame() {
        timer?.cancel()
        timer = nil
        state = .idle
    }

    private func startTimer() {
        timer?.cancel()
        timer = Timer.publish(every: tickRate, on: .main, in: .common)
            .autoconnect()
            .sink { [weak self] _ in
                self?.tick()
            }
    }

    private func tick() {
        guard state == .playing else { return }

        let dt = tickRate

        // Rotation
        if fuel > 0 && abs(rotationInput) > 0.01 {
            angularVelocity += rotationInput * 60.0 * dt
            fuel -= abs(rotationInput) * GameModel.fuelBurnRate * 0.3 * dt
        }
        angularVelocity *= 0.95  // damping
        angle += angularVelocity * dt
        angle = max(-45, min(45, angle))  // clamp angle

        // Thrust
        let effectiveThrust = fuel > 0 ? thrustLevel * GameModel.maxThrust : 0
        let angleRad = angle * .pi / 180.0
        let thrustX = effectiveThrust * sin(angleRad)
        let thrustY = effectiveThrust * cos(angleRad)

        if fuel > 0 && thrustLevel > 0.01 {
            fuel -= thrustLevel * GameModel.fuelBurnRate * dt
            fuel = max(0, fuel)
        }

        // Apply physics
        velocityY += (-GameModel.gravity + thrustY) * dt
        velocityX += thrustX * dt

        // Drag (atmospheric, minimal on moon but helps gameplay)
        velocityX *= 0.998
        velocityY *= 0.999

        // Update altitude
        altitude += velocityY * dt
        altitude = max(0, altitude)

        // Update screen position
        let altitudeRatio = altitude / GameModel.startAltitude
        positionY = 1.0 - altitudeRatio * 0.85 - 0.1
        positionX += (velocityX * dt) / 200.0
        positionX = max(0.05, min(0.95, positionX))

        // Check landing
        if altitude <= 0 {
            timer?.cancel()
            checkLanding()
        }
    }

    private func checkLanding() {
        let speed = sqrt(velocityX * velocityX + velocityY * velocityY)
        let onPad = abs(positionX - landingPadX) < landingPadWidth / 2
        let safeSpeed = speed <= GameModel.safeVelocity
        let safeAngleOk = abs(angle) <= GameModel.safeAngle

        if onPad && safeSpeed && safeAngleOk {
            state = .landed
            computeScore(speed: speed)
        } else {
            state = .crashed
        }
    }

    private func computeScore(speed: Double) {
        let speedBonus = Int((GameModel.safeVelocity - speed) * 100)
        let fuelBonus = Int(fuel * 10)
        let angleBonus = Int((GameModel.safeAngle - abs(angle)) * 20)
        score = max(0, speedBonus + fuelBonus + angleBonus)
    }
}
