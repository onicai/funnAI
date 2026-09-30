/**
 * Quarterly reward decreases from the minting schedule.
 *
 * Every decrease is 12:00 at a fixed UTC−8 offset, displayed as
 * "12pm PT / 9pm CET". The offset is shared by all events so the
 * clock does not shift between PST and PDT.
 */

export const REWARD_DECREASE_OFFSET = "-08:00";
export const REWARD_DECREASE_CLOCK_LABEL = "12pm PT / 9pm CET";

const MONTHS = [
  "Jan",
  "Feb",
  "Mar",
  "Apr",
  "May",
  "Jun",
  "Jul",
  "Aug",
  "Sept",
  "Oct",
  "Nov",
  "Dec",
] as const;

const ISO_DATE = /^(\d{4})-(\d{2})-(\d{2})$/;

export interface RewardSchedulePoint {
  date: string;
  rewards_per_challenge: number;
}

export interface ResolvedRewardSchedule {
  /** Reward in effect now, or null before the first decrease. */
  rewardPerChallenge: number | null;
  /** Next date the reward actually falls, as YYYY-MM-DD. */
  nextDecreaseDate: string | null;
  nextDecreaseAt: Date | null;
  /** True once the reward has leveled off and only a drop to zero remains. */
  stabilized: boolean;
  /** True after the schedule point that sets the reward to zero. */
  ended: boolean;
}

export function rewardDecreaseInstant(isoDate: string): Date {
  return new Date(`${isoDate}T12:00:00${REWARD_DECREASE_OFFSET}`);
}

export function formatRewardDecreaseWhen(isoDate: string): string {
  const match = ISO_DATE.exec(isoDate);
  if (!match) return `${isoDate} · ${REWARD_DECREASE_CLOCK_LABEL}`;
  const month = MONTHS[Number(match[2]) - 1] ?? match[2];
  const day = Number(match[3]);
  return `${month} ${day}, ${match[1]} · ${REWARD_DECREASE_CLOCK_LABEL}`;
}

export function formatRewardPerChallenge(value: number): string {
  return value.toFixed(2);
}

/**
 * Current reward is the latest schedule point that has already occurred.
 * The next decrease is the following point where the reward is lower and
 * still above zero. A later drop to zero (max supply) is not a decrease.
 */
export function resolveRewardSchedule(
  entries: RewardSchedulePoint[],
  now: Date = new Date()
): ResolvedRewardSchedule {
  const points = entries
    .filter((entry) => ISO_DATE.test(entry.date))
    .map((entry) => ({
      date: entry.date,
      at: rewardDecreaseInstant(entry.date),
      reward: Number(entry.rewards_per_challenge),
    }))
    .filter((entry) => !Number.isNaN(entry.at.getTime()) && Number.isFinite(entry.reward))
    .sort((a, b) => a.at.getTime() - b.at.getTime() || a.date.localeCompare(b.date));

  const nowMs = now.getTime();
  let current: (typeof points)[number] | null = null;
  for (const point of points) {
    if (point.at.getTime() <= nowMs) current = point;
  }

  const rewardPerChallenge = current ? current.reward : null;
  const next = points.find((point) => {
    if (point.at.getTime() <= nowMs) return false;
    if (point.reward <= 0) return false;
    if (rewardPerChallenge == null) return true;
    return point.reward < rewardPerChallenge;
  });

  return {
    rewardPerChallenge,
    nextDecreaseDate: next?.date ?? null,
    nextDecreaseAt: next?.at ?? null,
    stabilized: rewardPerChallenge != null && rewardPerChallenge > 0 && !next,
    ended: rewardPerChallenge === 0,
  };
}
