import { z } from "zod";
import { TaskStatus, AutonomyLevel, Provider, CredentialType } from "./enums";

/**
 * UUID schema
 */
export const UUID = z.string().uuid();

/**
 * ISO datetime string
 */
export const DateTimeString = z.string().datetime();

/**
 * Task schema - represents a unit of work for an AI agent
 */
export const Task = z.object({
  id: UUID,
  name: z.string().min(1).max(255),
  description: z.string().optional(),
  status: TaskStatus,
  teamMemberId: UUID,
  createdAt: DateTimeString,
  updatedAt: DateTimeString,
  startedAt: DateTimeString.optional(),
  completedAt: DateTimeString.optional(),
  metadata: z.record(z.unknown()).optional(),
});
export type Task = z.infer<typeof Task>;

/**
 * Team Member schema - represents an AI agent configuration
 */
export const TeamMember = z.object({
  id: UUID,
  name: z.string().min(1).max(255),
  description: z.string().optional(),
  modelId: UUID,
  autonomyLevel: AutonomyLevel,
  systemPrompt: z.string().optional(),
  tools: z.array(z.string()).default([]),
  createdAt: DateTimeString,
  updatedAt: DateTimeString,
});
export type TeamMember = z.infer<typeof TeamMember>;

/**
 * Model schema - represents an LLM model configuration
 */
export const Model = z.object({
  id: UUID,
  name: z.string().min(1).max(255),
  provider: Provider,
  modelId: z.string().min(1), // e.g., "claude-3-opus-20240229"
  maxTokens: z.number().int().positive().default(4096),
  temperature: z.number().min(0).max(2).default(1),
  credentialId: UUID.optional(),
  createdAt: DateTimeString,
  updatedAt: DateTimeString,
});
export type Model = z.infer<typeof Model>;

/**
 * Credential schema - represents stored API credentials
 */
export const Credential = z.object({
  id: UUID,
  name: z.string().min(1).max(255),
  type: CredentialType,
  provider: Provider,
  // Note: actual secret values are never exposed in API responses
  createdAt: DateTimeString,
  updatedAt: DateTimeString,
});
export type Credential = z.infer<typeof Credential>;

/**
 * User Settings schema
 */
export const UserSettings = z.object({
  id: UUID,
  userId: UUID,
  theme: z.enum(["light", "dark", "system"]).default("system"),
  defaultAutonomyLevel: AutonomyLevel.default("supervised"),
  notificationsEnabled: z.boolean().default(true),
  createdAt: DateTimeString,
  updatedAt: DateTimeString,
});
export type UserSettings = z.infer<typeof UserSettings>;

/**
 * API Health Response
 */
export const HealthResponse = z.object({
  status: z.enum(["ok", "error"]),
  version: z.string(),
});
export type HealthResponse = z.infer<typeof HealthResponse>;
