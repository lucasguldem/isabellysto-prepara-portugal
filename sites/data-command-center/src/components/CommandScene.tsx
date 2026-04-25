import { useMemo, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Billboard, Float, Grid, Line, OrbitControls, Text } from '@react-three/drei';
import * as THREE from 'three';
import { createCountrySceneLayout } from '../lib/commandCenter';
import type { CommandCenterSnapshot, CountrySceneNode, StoryModule } from '../types';

type CommandSceneProps = {
  snapshot: CommandCenterSnapshot;
  activeModule: StoryModule;
  unlocked: boolean;
  selectedCountry: string;
  onSelectCountry: (country: string) => void;
};

function CentralHub({ activeModule }: { activeModule: StoryModule }) {
  const group = useRef<THREE.Group>(null);
  useFrame((_, delta) => {
    if (group.current) group.current.rotation.y += delta * 0.26;
  });
  const color = activeModule === 'recommendations' ? '#a78bfa' : '#22d3ee';
  return (
    <group ref={group}>
      <mesh position={[0, 1.15, 0]}>
        <icosahedronGeometry args={[0.72, 2]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={1.65} wireframe transparent opacity={0.82} />
      </mesh>
      <mesh position={[0, 1.15, 0]}>
        <sphereGeometry args={[0.28, 32, 32]} />
        <meshStandardMaterial color="#f8fafc" emissive="#22d3ee" emissiveIntensity={0.9} />
      </mesh>
      <Line
        points={Array.from({ length: 80 }, (_, index) => {
          const angle = (index / 79) * Math.PI * 2;
          return [Math.cos(angle) * 1.25, 1.15, Math.sin(angle) * 1.25] as [number, number, number];
        })}
        color={color}
        lineWidth={1}
        transparent
        opacity={0.72}
      />
    </group>
  );
}

function CountryBar({
  node,
  selected,
  muted,
  onSelect,
}: {
  node: CountrySceneNode;
  selected: boolean;
  muted: boolean;
  onSelect: (country: string) => void;
}) {
  const mesh = useRef<THREE.Mesh>(null);
  useFrame((state) => {
    if (mesh.current) {
      mesh.current.scale.y = 1 + Math.sin(state.clock.elapsedTime * 1.5 + node.leads) * 0.025;
    }
  });
  const opacity = muted ? 0.28 : selected ? 1 : 0.72;
  const showLabel = selected || node.rank <= 5;
  return (
    <group>
      <mesh
        ref={mesh}
        position={node.position}
        onClick={() => onSelect(node.country)}
        onPointerOver={(event) => event.stopPropagation()}
      >
        <cylinderGeometry args={[node.radius, node.radius * 0.7, node.height, 8]} />
        <meshStandardMaterial
          color={node.color}
          emissive={node.color}
          emissiveIntensity={selected ? 1.9 : 1.15}
          transparent
          opacity={opacity}
          roughness={0.25}
          metalness={0.25}
        />
      </mesh>
      {showLabel && (
        <Billboard position={[node.position[0], node.height + 0.28, node.position[2]]}>
          <Text
            fontSize={selected ? 0.15 : 0.115}
            color={selected ? '#f8fafc' : node.color}
            anchorX="center"
            anchorY="middle"
            outlineWidth={0.006}
            outlineColor="#020617"
          >
            {node.country}
          </Text>
        </Billboard>
      )}
    </group>
  );
}

function CountryLayer({
  nodes,
  selectedCountry,
  activeModule,
  onSelectCountry,
}: {
  nodes: CountrySceneNode[];
  selectedCountry: string;
  activeModule: StoryModule;
  onSelectCountry: (country: string) => void;
}) {
  return (
    <group>
      {nodes.map((node) => (
        <CountryBar
          key={node.country}
          node={node}
          selected={node.country === selectedCountry}
          muted={activeModule === 'icp' && node.country !== selectedCountry}
          onSelect={onSelectCountry}
        />
      ))}
    </group>
  );
}

function PersonaMatrix({ snapshot, activeModule }: { snapshot: CommandCenterSnapshot; activeModule: StoryModule }) {
  const points = useMemo(() => {
    return snapshot.personas.flatMap((persona, roleIndex) =>
      snapshot.segments.map((segment, segmentIndex) => {
        const intensity = Math.max(persona.lead_share, 0.04) * Math.max(segment.lead_share, 0.04);
        return {
          key: `${persona.role_category}-${segment.company_size_segment}`,
          x: (roleIndex - snapshot.personas.length / 2) * 0.48,
          y: 0.45 + intensity * 8,
          z: 3.2 + segmentIndex * 0.42,
          radius: 0.05 + intensity * 0.28,
          color: roleIndex % 2 === 0 ? '#22d3ee' : '#a78bfa',
        };
      }),
    );
  }, [snapshot.personas, snapshot.segments]);

  return (
    <group visible={activeModule === 'icp' || activeModule === 'unlocked'}>
      {points.map((point) => (
        <Float key={point.key} speed={1.2} rotationIntensity={0.3} floatIntensity={0.45}>
          <mesh position={[point.x, point.y, point.z]}>
            <sphereGeometry args={[point.radius, 18, 18]} />
            <meshStandardMaterial color={point.color} emissive={point.color} emissiveIntensity={1.35} transparent opacity={0.75} />
          </mesh>
        </Float>
      ))}
    </group>
  );
}

function RecommendationArcs({ nodes, activeModule }: { nodes: CountrySceneNode[]; activeModule: StoryModule }) {
  const visible = activeModule === 'recommendations' || activeModule === 'unlocked';
  return (
    <group visible={visible}>
      {nodes.slice(0, 8).map((node, index) => (
        <Line
          key={node.country}
          points={[
            [0, 1.25, 0],
            [node.position[0] * 0.45, 2.15 + index * 0.04, node.position[2] * 0.45],
            [node.position[0], node.height + 0.2, node.position[2]],
          ]}
          color={node.color}
          lineWidth={1.4}
          transparent
          opacity={0.45}
        />
      ))}
    </group>
  );
}

export default function CommandScene({
  snapshot,
  activeModule,
  unlocked,
  selectedCountry,
  onSelectCountry,
}: CommandSceneProps) {
  const nodes = useMemo(() => createCountrySceneLayout(snapshot.market), [snapshot.market]);

  return (
    <div className="scene-stage" data-testid="scene-stage">
      <Canvas
        data-testid="command-canvas"
        camera={{ position: unlocked ? [4.6, 5.8, 8.5] : [4.1, 4.9, 7.7], fov: 40 }}
        dpr={[1, 1.45]}
        gl={{ antialias: true, alpha: false, preserveDrawingBuffer: true }}
        onCreated={({ gl }) => gl.setClearColor('#020617')}
      >
        <fog attach="fog" args={['#020617', 7, 17]} />
        <ambientLight intensity={0.32} />
        <pointLight position={[0, 6, 0]} intensity={85} color="#22d3ee" />
        <pointLight position={[-4, 4, 5]} intensity={45} color="#a78bfa" />
        <Grid
          args={[18, 18]}
          cellSize={0.72}
          cellThickness={0.55}
          sectionSize={3.6}
          sectionThickness={1.1}
          cellColor="#12304f"
          sectionColor="#22d3ee"
          fadeDistance={16}
          fadeStrength={1.4}
          position={[0, -0.02, 0]}
        />
        <group position={[0, -0.18, -0.35]}>
          <CentralHub activeModule={activeModule} />
          <CountryLayer
            nodes={nodes}
            selectedCountry={selectedCountry}
            activeModule={activeModule}
            onSelectCountry={onSelectCountry}
          />
          <PersonaMatrix snapshot={snapshot} activeModule={activeModule} />
          <RecommendationArcs nodes={nodes} activeModule={activeModule} />
        </group>
        {unlocked && <OrbitControls target={[0, 1.1, 0]} enablePan={false} minDistance={5} maxDistance={14} maxPolarAngle={Math.PI / 2.05} />}
      </Canvas>
    </div>
  );
}
