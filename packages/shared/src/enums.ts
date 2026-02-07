import { z } from "zod";

/**
 * Task execution status
 */
export const TaskStatus = z.enum([
  "pending",
  "running",
  "paused",
  "completed",
  "failed",
  "cancelled",
]);
export type TaskStatus = z.infer<typeof TaskStatus>;

/**
 * Level of autonomy for AI agents
 */
export const AutonomyLevel = z.enum([
  "supervised", // Requires approval for all actions
  "semi", // Requires approval for significant actions
  "autonomous", // Can act independently within bounds
]);
export type AutonomyLevel = z.infer<typeof AutonomyLevel>;

/**
 * LLM Provider
 */
export const Provider = z.enum([
  "anthropic",
  "openai",
  "google",
  "custom",
]);
export type Provider = z.infer<typeof Provider>;

/**
 * Credential type
 */
export const CredentialType = z.enum([
  "api_key",
  "oauth",
  "service_account",
]);
export type CredentialType = z.infer<typeof CredentialType>;
