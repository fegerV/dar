package com.daragent.domain.model

data class ReferralCode(
    val code: String,
    val uses: Int,
    val maxUses: Int?,
    val isActive: Boolean,
)

data class Referral(
    val id: String,
    val referrerUserId: String,
    val referredUserId: String?,
    val code: String,
    val status: String,
    val referrerBonusGranted: Boolean,
    val refereeBonusGranted: Boolean,
    val createdAt: String,
)

data class ReferralStats(
    val referralCode: String?,
    val totalReferrals: Int,
    val completedReferrals: Int,
    val referrerBonusGranted: Int,
    val refereeBonusGranted: Int,
    val earnedRub: Double,
    val referrerBonusRub: Double,
    val refereeBonusRub: Double,
)
