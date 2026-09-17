package com.daragent.data.repository

import com.daragent.data.network.api.ReferralsApi
import com.daragent.domain.model.ReactionStats
import com.daragent.domain.model.Referral
import com.daragent.domain.model.ReferralCode
import com.daragent.domain.model.ReferralStats
import com.daragent.domain.repository.ReferralRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class ReferralRepositoryImpl(
    private val api: ReferralsApi,
) : ReferralRepository {
    override suspend fun getMyCode(): Result<ReferralCode> = withContext(Dispatchers.IO) {
        runCatching {
            val resp = api.getMyCode()
            val dto = resp.body() ?: return@runCatching ReferralCode(
                code = "",
                uses = 0,
                maxUses = null,
                isActive = true,
            )
            dto.toDomain()
        }
    }

    override suspend fun applyCode(code: String): Result<Referral> = withContext(Dispatchers.IO) {
        runCatching {
            val resp = api.applyCode(mapOf("code" to code))
            resp.body()!!.toDomain()
        }
    }

    override suspend fun getStats(): Result<ReferralStats> = withContext(Dispatchers.IO) {
        runCatching {
            val resp = api.getStats()
            resp.body()!!.toDomain()
        }
    }
}

fun com.daragent.data.network.dto.ReferralCodeResponseDto.toDomain(): ReferralCode {
    return ReferralCode(
        code = code,
        uses = uses_count,
        maxUses = max_uses,
        isActive = is_active,
    )
}

fun com.daragent.data.network.dto.ReferralResponseDto.toDomain(): Referral {
    return Referral(
        id = id,
        referrerUserId = referrer_user_id,
        referredUserId = referred_user_id,
        code = code,
        status = status,
        referrerBonusGranted = referrer_bonus_granted,
        refereeBonusGranted = referee_bonus_granted,
        createdAt = created_at,
    )
}

fun com.daragent.data.network.dto.ReferralStatsResponseDto.toDomain(): ReferralStats {
    return ReferralStats(
        referralCode = referral_code,
        totalReferrals = total_referrals,
        completedReferrals = completed_referrals,
        referrerBonusGranted = referrer_bonus_granted,
        refereeBonusGranted = referee_bonus_granted,
        earnedRub = earned_rub,
        referrerBonusRub = referrer_bonus_rub,
        refereeBonusRub = referee_bonus_rub,
    )
}
